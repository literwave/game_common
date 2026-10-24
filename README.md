# game_common

游戏配置表仓库。`tsv/` 是源表，由 [星图](https://github.com/literwave/vis_conf) 导出为客户端 JSON 和服务端 Lua。

## 目录

| 路径 | 内容 |
|---|---|
| `tsv/` | 配置源表，UTF-8 TSV |
| `client/res/` | 前端导出，JSON |
| `server/res/` | 后端导出，Lua |
| `vis_conf/` | 星图导表工具，submodule，跟踪 `main` |

## 克隆

```powershell
git clone --recurse-submodules git@github.com:literwave/game_common.git
```

如果已经克隆过、`vis_conf/` 是空的：

```powershell
git submodule update --init --recursive
```

## 改表并导出

在 `vis_conf/` 里启动星图，把配置文件目录设为仓库的 `tsv/`。前端导出到 `client/res/`（JSON），后端导出到 `server/res/`（Lua）。工具的安装、编辑和导表规则见 [vis_conf/README.md](vis_conf/README.md)。用 Cursor 改表前，先按 [配置 Cursor](vis_conf/README.md#配置-cursor) 安装 CLI 并在星图里选 Agent 模式。星图仍提示找不到 CLI，或要重装命令行时，按 [重装 CLI](vis_conf/README.md#重装-cli) 只删除 `%LOCALAPPDATA%\cursor-agent` 再装。不要删除 Cursor 编辑器或 `%USERPROFILE%\.cursor`。

图标在表格里显示为缩略图。打开「导出设置」，把「UI 配置目录」设为客户端的 UI 资源目录，例如 `D:\code\game_demo_client\assets\resources\ui`。单元格写成下面这种路径时，会到该目录下找图片：

```json
{
  "Id": 3,
  "Name": "加速令",
  "Icon": "ui/item_icons/speed_up"
}
```

`Icon` 对应 `D:\code\game_demo_client\assets\resources\ui\item_icons\speed_up.png`。扩展名可以不写，末尾的 `/spriteFrame` 也会去掉。

改完后一起提交这三处：`tsv/`、`client/res/`、`server/res/`。不要只提交导出结果。

每个 TSV 前四行是元数据：字段名、数据类型、导出端、字段注释，第 5 行起是数据。导出端为 `both` 的字段会同时出现在前后端；`frontend` 只进 JSON，`backend` 只进 Lua。

## 配置表

| 表 | 说明 |
|---|---|
| `BuildingDetail` | 建筑类型；`Type` 1主城/2军事/3资源/4功能/5防御；`Icon` 只导出到前端；`Id` 1 为主城（任务 `bid` 对齐） |
| `BuildingLv` | 建筑等级；粮/木/铁消耗、升级时间、前置与效果值；`BuildingType` 指向 `BuildingDetail.Id` |
| `Global` | 全局常量；`Id=1` 初始奖励（`reward_type`：1道具/3武将/4兵力），`Id=2` 初始武将，`Id=8` 最大兵力（`value1`） |
| `HeadIcon` | 头像资源 |
| `Hero` | 武将；`Resources` / `Icon` / `name` 只导出到前端；`SkillId` 指向 `Skill.Id`；升级经验见 `HeroLv` |
| `HeroLv` | 武将升级；全武将共用；`Exp` 为升到下一级所需经验，满级为 0 |
| `Skill` | 技能；`Icon` 只导出到前端；武将通过 `SkillId` 关联 |
| `Item` | 道具；`Kind` 1粮草/2木材/3铁矿/4令牌/5加速/6特殊；`Icon`/`Desc` 只导出到前端；加速类 `useParams.time` 为秒数 |
| `Lottery` | 抽卡消耗与卡池 |
| `ReportInfo` | 后台域名和端口 |
| `ServerGroup` | 服务器群组与后台 ID |
| `SystemOpen` | 系统开启；当前为更换头像 |
| `EntityType` | AOI 实体类型枚举；对齐 `world.proto` 的 `entityType`：1主城/2行军部队/3怪物组 |
| `TargetType` | 行军目标类型枚举；对齐 `world.proto` 的 `targetType`：1回城/2打怪 |
| `MainTask` | 主线任务；`NextId` 衔接下一任务；`Cond` 为 `{ type, ...参数 }`；`Icon`/`Desc`/`Jump` 只导出到前端；协议见 `proto/task.proto`（`taskType=1`） |
| `DailyTask` | 日常任务；每日重置；字段同主线但无 `NextId`；协议 `taskType=2` |
| `WeekTask` | 周常任务；每周重置；字段同日常；协议 `taskType=3` |
| `Activity` | 活动；`Type` 1登录/2冲榜/3限时招募/4资源增产/5礼包/6在线/7兑换；`Time` 为 `{ type, ...参数 }`；`OpenCond`/`Params`/`Rewards` 按类型解释；`Icon`/`Desc`/`Jump` 只导出到前端；协议见 `proto/activity.proto` |
| `Monster` | 怪物单位；战斗属性对齐武将；`Soldier` 兵力、`Power` 战力；`SkillId` 可选；`Icon`/`Desc` 只导出到前端 |
| `MonsterGroup` | 怪物组（地图贼寇/山寨/首领）；`Type` 1贼寇/2山寨/3首领；`Monsters` 为 `{ mid, pos }` 阵容（`mid`→`Monster.Id`）；`Reward` 同任务奖励格式；`Refresh` 刷新秒数；`OpenCond` 如 `{ level = 1 }` |
