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
| `BuildingDetail` | 建筑类型；`Type` 1主城/2军事/3资源/4功能/5防御；资源建筑含农场/伐木/铁矿/采石场（`Id=16`，`OutputItem=4` 石料）；`Icon` 只导出到前端；`Id` 1 为主城（任务 `bid` 对齐） |
| `BuildingLv` | 建筑等级；粮/木/铁/石消耗、前置与效果值（建造/升级即时完成，无时间）；`BuildingType` 指向 `BuildingDetail.Id`；协议见 `proto/build.proto` |
| `Global` | 全局常量；`Id=1` 初始奖励（`reward_type`：1道具/3武将/4兵力），`Id=2` 初始武将，`Id=8` 最大兵力（`value1`），`Id=9` 单频道最大聊天记录条数（`value1`）；联盟相关：`Id=10` 创建消耗令牌数（道具 Id=100），`Id=11` 名称最大长度，`Id=12` 公告最大长度，`Id=13` 宣言最大长度，`Id=14` 申请列表上限；邮件：`Id=15` 单类型最大邮件条数，`Id=16` 默认邮件保留天数（`Mail.ExpireDay=0` 时用）；行军：`Id=17` 行军速度（每秒移动格数，`value1`，用于按路径长度算 `endTime`）；地图标记：`Id=18` 标记点上限（`value1`，协议见 `world.proto`）；创建开启条件见 `SystemOpen.CREATE_ALLIANCE`；人数上限见 `AllianceLv` |
| `ChatChannel` | 聊天频道枚举；对齐 `chat.proto` 的 `channel`：1世界/2联盟/3私聊；协议见 `proto/chat.proto` |
| `MailKind` | 邮件类型枚举；对齐 `mail.proto` 的 `mailKind`：1系统/2联盟/3公告 |
| `Mail` | 邮件模板；`Kind`→`MailKind`；协议 `mailId`→`Mail.Id`，实例唯一 id 为 `mailUid`；`Title`/`Content` 中 `%s` 由详情 `detailList` 替换；不配奖励，有奖时发信填协议 `rewardList`；`Icon`/`Sender` 只导出到前端；协议见 `proto/mail.proto` |
| `AlliancePos` | 联盟职位枚举；对齐 `alliance.proto` 的 `pos`：1盟主/2官员/3成员；协议见 `proto/alliance.proto` |
| `AllianceJoinType` | 联盟加入方式枚举；对齐 `alliance.proto` 的 `joinType`：1自由加入/2需审批/3禁止加入 |
| `AllianceLv` | 联盟等级；`MemberMax` 人数上限、`OfficerMax` 官员上限（不含盟主）、`Exp` 升到下一级所需贡献（满级为 0）；`memberMax` 协议字段取当前等级的 `MemberMax` |
| `HeadIcon` | 头像资源 |
| `Hero` | 武将；`Resources` / `Icon` / `name` 只导出到前端；`SkillId` 指向 `Skill.Id`；`Convert` 为已有武将重复获得时转奖励（同任务 `Reward`：`reward_type`/`item_id`/`item_count`，碎片 `item_id=10000+Hero.Id`）；升级经验见 `HeroLv` |
| `HeroLv` | 武将升级；全武将共用；`Exp` 为升到下一级所需经验，满级为 0 |
| `Skill` | 技能；`Icon` 只导出到前端；武将通过 `SkillId` 关联 |
| `Item` | 道具；`Id` 1–4 四资源（粮/木/铁/石），`5–99` 预留资源扩展，`100` 令牌（建盟/兑换），`101` 训练加速，`102` 治疗加速，`103` 点将符（招募），`1001` 迁城令，`11001+` 武将碎片（`Id=10000+Hero.Id`，`useParams.hero_id`）；`Kind` 1粮草/2木材/3铁矿/4石料/5加速/6特殊/7令牌/8武将碎片/9点将符；`Quality` 品质（只导出到前端；碎片对齐武将 `Star`）；`Icon`/`Desc`/`Quality` 只导出到前端；加速类 `useParams.time` 为秒数（建筑无耗时，无建造加速）；协议见 `proto/item.proto`（`req_all_item_data` 拉取快照，`sync_item_data` 单条同步） |
| `Lottery` | 抽卡；`Id=1` 单抽 / `Id=10` 十连；`CostList` 消耗点将符（`item_id=103`）；`CommonPools`/`HeroPools` 为带 `weight` 的奖励列表（同 `reward_type`：1道具/3武将）；抽奖先按两池 `weight` 总和选池，再在池内加权；约 85% 普通（资源/令牌/加速/碎片）+ 15% 武将（2★>3★>4★>5★） |
| `ReportInfo` | 后台域名和端口 |
| `ServerGroup` | 服务器群组与后台 ID |
| `SystemOpen` | 系统开启；`HEAD_ICON` 更换头像、`CREATE_ALLIANCE` 创建联盟（`Cond.level` 控制开启主城等级） |
| `Errcode` | 错误码枚举；后端下发 `Id`，前端用 `Msg` 提示；`Name`/`Msg` 只导出到前端 |
| `EntityType` | AOI 实体类型枚举；对齐 `world.proto` 的 `entityType`：1主城/2行军部队/3怪物组/4资源地 |
| `TargetType` | 行军目标类型枚举；对齐 `world.proto` / 战报 `targetType`：1回城/2打怪/3占领资源地/4移动 |
| `TroopState` | 部队状态枚举：0在城/1行军/2停留/3采集 |
| `ReportType` | 战报类型枚举；对齐 `report.proto` / `battle.proto` 的 `reportType`：1打怪/2攻打玩家/3防守/4占领资源地 |
| `RankType` | 排行榜类型枚举；对齐 `rank.proto` 的 `rankType` / Activity `Params.rank_type`：1战力/2主城等级；协议见 `proto/rank.proto`（打开时拉取，无实时推送） |
| `MainTask` | 主线任务；`NextId` 衔接下一任务；`Cond` 为 `{ type, ...参数 }`；`Icon`/`Desc`/`Jump` 只导出到前端；协议见 `proto/task.proto`（`taskType=1`） |
| `DailyTask` | 日常任务；每日重置；字段同主线但无 `NextId`；协议 `taskType=2` |
| `WeekTask` | 周常任务；每周重置；字段同日常；协议 `taskType=3` |
| `Activity` | 活动；`Type` 1登录/2冲榜/3限时招募/4资源增产/5礼包/6在线/7兑换；冲榜类 `Params.rank_type` → `RankType.Id`；`Time` 为 `{ type, ...参数 }`；`OpenCond`/`Params`/`Rewards` 按类型解释；`Icon`/`Desc`/`Jump` 只导出到前端；协议见 `proto/activity.proto` |
| `Monster` | 怪物单位；战斗属性对齐武将；`Soldier` 兵力、`Power` 战力；`SkillId` 可选；`Icon`/`Desc` 只导出到前端 |
| `MonsterGroup` | 怪物组（地图贼寇/山寨/首领）；`Type` 1贼寇/2山寨/3首领；`Monsters` 为 `{ mid, pos }` 阵容（`mid`→`Monster.Id`）；`Reward` 同任务奖励格式；`Refresh` 刷新秒数；`OpenCond` 如 `{ level = 1 }`；打怪战报/回放见 `proto/report.proto`，战斗流程见 `proto/battle.proto` |
| `ResLandType` | 资源地类型枚举；对齐 `ResLand.Type`：1粮田/2林场/3铁矿/4石场（产出对应 Item 1/2/3/4） |
| `ResLand` | 资源地；`Id=Type*100+Level`；`Capacity`/`GatherSpeed` 为占领后采集；`MonsterGroups` 占领时等权随机守卫；`Reward` 击败守卫后立即发放（无占领倒计时）；`OpenCond` 如 `{ level = 1 }`；行军 `TargetType=OCCUPY_RES_LAND`；`Icon`/`Desc` 只导出到前端 |
