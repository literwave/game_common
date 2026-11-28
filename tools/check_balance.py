"""Read-only configuration checks. Run: python tools/check_balance.py."""
from pathlib import Path
import collections
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'vis_conf'))
from table_file import load_table
from export_data import prepare_export_files, load_directory_key_rules

TABLES = {p.stem: load_table(p) for p in (ROOT / 'tsv').glob('*.tsv')}


def rows(name):
    return TABLES[name][4]


def resource_rewards(rewards):
    total = collections.Counter()
    for reward in rewards:
        if reward['reward_type'] == 1 and reward.get('item_id') in (1, 2, 3, 4):
            total[reward['item_id']] += reward['item_count']
    return total


class BalanceChecks(unittest.TestCase):
    def test_building_levels_and_reachable_storage(self):
        details = {r['Id']: r for r in rows('BuildingDetail')}
        levels = {(r['BuildingType'], r['Lv']): r for r in rows('BuildingLv')}
        for bid, detail in details.items():
            self.assertEqual(sorted(lv for b, lv in levels if b == bid),
                             list(range(1, detail['MaxLevel'] + 1)))
        # Simulate prerequisites AND saving enough resources before each purchase.
        # This detects a warehouse requiring its own larger capacity to upgrade.
        current = {bid: r['InitLev'] for bid, r in details.items()}
        active = set()

        def ensure(bid, target):
            if current[bid] >= target:
                return
            self.assertNotIn((bid, target), active, 'unreachable prerequisite/storage cycle')
            active.add((bid, target))
            if current[bid] == 0:
                for req in details[bid]['CreateLimit'] or []:
                    ensure(req['bid'], req['lev'])
            while current[bid] < target:
                row = levels[(bid, current[bid] + 1)]
                for req in row['UpgradeLimit'] or []:
                    ensure(req['bid'], req['lev'])
                cost = max(row[k] for k in ('CostGrain', 'CostWood', 'CostIron', 'CostStone'))
                if cost:
                    capable = [lv for (b, lv), r in levels.items() if b == 13 and r['Effect'] >= cost]
                    self.assertTrue(capable, f'no storage for building {bid}, level {row["Lv"]}')
                    ensure(13, min(capable))
                current[bid] += 1
            active.remove((bid, target))

        for bid, detail in details.items():
            ensure(bid, detail['MaxLevel'])
        barracks = [r for r in details.values() if r['EffectType'] == 4]
        self.assertEqual([r['Id'] for r in barracks], [4])
        self.assertEqual(barracks[0]['Name'], '兵营')
        self.assertEqual(
            [levels[(4, lv)]['Effect'] for lv in range(1, 11)],
            [250 + (lv - 1) * 100 for lv in range(1, 11)],
        )
        self.assertNotIn(5, details)
        self.assertNotIn(6, details)
        effect_ids = {r['Id'] for r in rows('EffectType')}
        self.assertEqual(effect_ids, {2, 3, 4, 5, 7, 8, 9})
        for detail in details.values():
            if detail['EffectType']:
                self.assertIn(detail['EffectType'], effect_ids)
        globals_ = {r['Id']: r for r in rows('Global')}
        self.assertEqual(globals_[22]['value1'], 8)

    def test_opening_budget_requires_progression(self):
        globals_ = {r['Id']: r for r in rows('Global')}
        initial = resource_rewards(globals_[1]['value2'])
        first = next(r for r in rows('MainTask') if r['Id'] == 1001)
        budget = initial + resource_rewards(first['Reward'])
        levels = {(r['BuildingType'], r['Lv']): r for r in rows('BuildingLv')}
        # The opening grants cover the palace-3 tutorial, but cannot fund even
        # palace-only progression to level 5 (which also has other prerequisites).
        for item, field in enumerate(('CostGrain', 'CostWood', 'CostIron', 'CostStone'), 1):
            self.assertGreaterEqual(budget[item], sum(levels[(1, lv)][field] for lv in (2, 3)))
        self.assertLess(budget[1], sum(levels[(1, lv)]['CostGrain'] for lv in range(2, 6)))
        reserve = sum(r['item_count'] for r in globals_[1]['value2'] if r['reward_type'] == 4)
        self.assertLessEqual(reserve, globals_[8]['value1'])

    def test_monster_progression_and_references(self):
        monsters = {r['Id']: r for r in rows('Monster')}
        groups = {r['Id']: r for r in rows('MonsterGroup')}
        last_soldiers = last_power = last_reward = 0
        for group in sorted((r for r in groups.values() if r['Type'] == 1), key=lambda r: r['Level']):
            units = [monsters[u['mid']] for u in group['Monsters']]
            self.assertEqual(len(group['Monsters']), len({u['pos'] for u in group['Monsters']}))
            soldiers = sum(u['Soldier'] for u in units)
            power = sum(u['Power'] for u in units)
            reward = sum(resource_rewards(group['Reward']).values())
            self.assertGreater(soldiers, last_soldiers)
            self.assertGreater(power, last_power)
            self.assertGreater(reward, last_reward)
            last_soldiers, last_power, last_reward = soldiers, power, reward
        for land in rows('ResLand'):
            self.assertTrue(land['MonsterGroups'])
            self.assertTrue(set(land['MonsterGroups']) <= groups.keys())
        for city in rows('City'):
            self.assertTrue(all(u['mid'] in monsters for u in city['Team']))

    def test_rewards_and_task_chain(self):
        lands = {(r['Type'], r['Level']): r for r in rows('ResLand')}
        firsts = {(r['Type'], r['Level']): r for r in rows('ResLandFirst')}
        self.assertEqual(lands.keys(), firsts.keys())
        for key, first in firsts.items():
            reward = resource_rewards(first['Reward'])
            speed = lands[key]['GatherSpeed']
            self.assertGreater(reward[key[0]], 0)
            self.assertLessEqual(reward[key[0]], speed * 3)
            self.assertLessEqual(sum(reward.values()), speed * 5)
        for table in ('DailyTask', 'WeekTask'):
            for task in rows(table):
                if task['Cond']['type'] == 4:
                    tickets = sum(r['item_count'] for r in task['Reward']
                                  if r['reward_type'] == 1 and r.get('item_id') == 103)
                    self.assertLess(tickets, task['Target'], 'repeatable full ticket refund')
        tasks = {r['Id']: r for r in rows('MainTask')}
        current = min(tasks, key=lambda key: tasks[key]['Order'])
        visited = set()
        while current:
            self.assertIn(current, tasks)
            self.assertNotIn(current, visited)
            visited.add(current)
            current = tasks[current]['NextId']
        self.assertEqual(visited, tasks.keys())

    def test_source_export_consistency(self):
        rules = load_directory_key_rules(str(ROOT / 'tsv'))
        reviewed = ('Global', 'Guide', 'BuildingDetail', 'BuildingLv', 'EffectType', 'MainTask', 'DailyTask',
                    'WeekTask', 'Activity', 'ResLand', 'ResLandFirst', 'Monster',
                    'MonsterGroup', 'Lottery', 'Hero', 'HeroLv', 'Skill', 'City', 'Item')
        for name in reviewed:
            columns, types, targets, _, data = TABLES[name]
            for path, content in prepare_export_files(
                columns, types, targets, data, name + '.tsv', 'lua', 'json',
                str(ROOT / 'server/res'), str(ROOT / 'client/res'),
                rules.get(name + '.tsv', []), validate_directories=False,
            ):
                self.assertEqual(path.read_bytes(), content, str(path.relative_to(ROOT)))
        self.assertNotIn('Reward', TABLES['ResLand'][0])


if __name__ == '__main__':
    unittest.main(verbosity=2)
