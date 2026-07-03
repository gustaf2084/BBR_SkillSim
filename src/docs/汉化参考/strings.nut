::MSU.Table.merge(::Const.Strings.PerkName, {
	RF_Angler = "捕鱼好手",
	RF_BattleFervor = "战斗热忱",
	RF_BackToBasics = "返朴归真",
	RF_CalculatedStrikes = "预判打击",
	RF_CheapTrick = "卑鄙手段",
	RF_Command = "发号施令",
	RF_Skirmisher = "散兵",
	RF_BearDown = "疲敌制胜",
	RF_BestialVigor = "野性活力",
	RF_BetweenTheEyes = "直抵眉心",
	RF_BetweenTheRibs = "直插软肋",
	RF_Blitzkrieg = "闪电战",
	RF_Bloodlust = "嗜血",
	RF_DeathDealer = "死亡使者",
	RF_Bolster = "精神支撑",
	RF_BoneBreaker = "碎骨者",
	RF_Bully = "威压",
	RF_Bulwark = "堡垒",
	RF_Finesse = "技艺",
	RF_Centurion = "百夫长",
	RF_Combo = "连击",
	RF_ConcussiveStrikes = "震荡打击",
	RF_Decanus = "十夫长",
	RF_Decisive = "果决",
	RF_DeepCuts = "深度切割",
	RF_DeepImpact = "深度震击",
	RF_DentArmor = "击凹护甲",
	RF_DiscoveredTalent = "发掘潜能",
	RF_Dismantle = "拆除",
	RF_Dismemberment = "肢解",
	RF_DoubleStrike = "双重打击",
	RF_DynamicDuo = "灵动二人组",
	RF_EnGarde = "接战势",
	RF_Entrenched = "稳固",
	RF_ExploitOpening = "直取空门",
	RF_ExudeConfidence = "自信流露",
	RF_FailedPotential = "失却潜力",
	RF_FamilyPride = "家族自豪感",
	RF_Fencer = "击剑手",
	RF_FeralRage = "野性之怒",
	RF_FlailSpinner = "链枷飞旋",
	RF_FlamingArrows = "燃烧箭",
	RF_FollowUp = "紧随其后",
	RF_FormidableApproach = "猛进疾退",
	RF_FreshAndFurious = "充沛激情",
	RF_FromAllSides = "四处发难",
	RF_FruitsOfLabor = "劳动成果",
	RF_Ghostlike = "行如鬼魅",
	RF_HaleAndHearty = "酣畅淋漓",
	RF_TrickstersPurses = "捣鬼腰包",
	RF_HipShooter = "腰射",
	RF_HoldSteady = "稳住阵线",
	RF_Hybridization = "融会贯通",
	RF_Supporter = "支持者",
	InspiringPresence = "勇气化身",
	RF_IronSights = "铁照门",
	RF_Kingfisher = "一网打尽",
	RF_KingOfAllWeapons = "百兵之王",
	RF_Legatus = "军团长",
	RF_Leverage = "杠杆作用",
	RF_LineBreaker = "破阵者",
	RF_Poise = "稳健",
	RF_LongReach = "枪长所及",
	RF_ManOfSteel = "钢铁之躯",
	RF_Marksmanship = "射击技术",
	RF_Mauler = "重击手",
	RF_Menacing = "咄咄逼人",
	RF_Mentor = "导师",
	RF_NailedIt = "射石饮羽",
	RF_OffhandTraining = "副手训练",
	RF_Opportunist = "伺机而动",
	RF_PassingStep = "跨步",
	RF_PatternRecognition = "洞悉招数",
	RF_Phalanx = "密集阵型",
	RF_Professional = "职业士兵",
	RF_PromisedPotential = "预期潜力",
	RF_Onslaught = "冲击阵线",
	RF_Rattle = "颤栗",
	RF_RealizedPotential = "觉醒潜力",
	RF_Rebuke = "迎击",
	RF_RisingStar = "冉冉新星",
	RF_Sanguinary = "嗜杀成性",
	RF_SavageStrength = "浑身蛮力",
	RF_SecondWind = "重振精神",
	RF_ShieldSergeant = "盾阵军士",
	RF_SmallTarget = "些小目标",
	RF_SoulLink = "灵魂链接",
	RF_SteadyBrace = "稳固射击",
	RF_StrengthInNumbers = "人多势众",
	RF_SurvivalInstinct = "生存本能",
	RF_SweepingStrikes = "横扫打击",
	RF_SwiftStabs = "迅捷连刺",
	RF_SwordmasterBladeDancer = "刀锋舞者",
	RF_SwordmasterGrappler = "摔跤手",
	RF_SwordmasterJuggernaut = "巨力",
	RF_SwordmasterMetzger = "屠夫",
	RF_SwordmasterPrecise = "精准",
	RF_SwordmasterReaper = "收割者",
	RF_SwordmasterVersatileSwordsman = "全能剑客",
	RF_TargetPractice = "标靶练习",
	RF_Tempo = "引领节奏",
	RF_TerrifyingVisage = "恐惧之容",
	RF_TheRushOfBattle = "战斗之潮",
	RF_ThroughTheGaps = "无缝不入",
	RF_ThroughTheRanks = "掠阵而过",
	RF_TrickShooter = "花样射手",
	RF_TripArtist = "陷绊艺术",
	RF_Unstoppable = "不歇之力",
	RF_Vanquisher = "征服者",
	RF_Retribution = "加倍奉还",
	RF_VengefulSpite = "复仇之怒",
	RF_Vigilant = "时刻提防",
	RF_VigorousAssault = "迅猛突袭",
	RF_WeaponMaster = "十八般兵器",
	RF_WearThemDown = "疲累打击",
	RF_WearsItWell = "量体裁衣",
	RF_WhirlingDeath = "死亡旋风"
});

local vanillaDescriptions = [
	{
		ID = "perk.battle_forged",
		Key = "BattleForged",
		Description = ::UPD.getDescription({
			Fluff = "重甲专精！",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"受到的护甲伤害减少，减少的百分比等于盔甲和头盔实时总护甲值之和的[color=" + ::Const.UI.Color.PositiveValue + "]5%[/color]。",
					"攻击具有[触及劣势|Concept.ReachDisadvantage]的角色时，每有300点头身护甲总值，无视1点触及劣势。"
					"不影响精神攻击和状态效果的伤害。",
					"拥有[$ $|Perk+perk_nimble]或[$ $|Perk+perk_rf_poise]后无法学习。"
				]
			}]
		})
	},
	{
		ID = "perk.bullseye",
		Key = "Bullseye",
		Description = ::UPD.getDescription({
			Fluff = "中！",
			Requirement = "远程武器",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"当瞄准弹道受阻的目标时，受到的命中惩罚从" + ::MSU.Text.colorNegative("75%") + "降至" + ::MSU.Text.colorNegative("50%") + "。",
					"攻击没有掩体的目标时，若使用弓，伤害穿甲率提高" + ::MSU.Text.colorPositive("+10%") + "，否则，提高" + ::MSU.Text.colorPositive("+20%") + "。"
				]
			}]
		})
	},
	{
		ID = "perk.rotation",
		Key = "Rotation",
		Description = ::UPD.getDescription({
			Fluff = "谁说佣兵不会跳舞。",
			Effects = [{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rotation]技能，该技能允许角色无视[控制区|Concept.ZoneOfControl]，与一个直接相邻的盟友交换位置。",
					"无法在任一角色被[$ $|Skill+stunned_effect]、[$ $|Skill+rooted_effect]或以其他方式失能时使用。"
				]
			}]
		})
	},
	{
		ID = "perk.fearsome",
		Key = "Fearsome",
		Description = ::UPD.getDescription({
			Fluff = "打得他们四散奔逃！",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"你的触发敌人[士气检定|Concept.Morale]的伤害阈值降为1。",
					"这些士气检定中，敌人受到你[决心|Concept.Resolve]" + ::MSU.Text.colorPositive("20%") + "的减值。"
				]
			}]
		})
	},
	{
		ID = "perk.footwork",
		Key = "Footwork",
		Description = ::UPD.getDescription({
			Fluff = "从对手的手心里溜走！",
			Effects = [
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+footwork]技能，该技能允许你离开[控制区|Concept.ZoneOfControl]而不受到借机攻击。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_sprint_skill]技能，该技能允许你在自己[回合|Concept.Turn]中走得更远。"
					]
				}
			]
		})
	},
	{
		ID = "perk.rally_the_troops",
		Key = "RallyTheTroops",
		Description = ::UPD.getDescription({
			Fluff = "一支友军号角持续激励着人们的勇气。",
			Effects = [{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rally_the_troops]技能，该技能可将附近所有队友的[士气|Concept.Morale]到相对稳定的等级。",
					"使用技能的角色[决心|Concept.Bravery]越高，成功的几率就越高。"
				]
			}]
		})
	},
	{
		ID = "perk.adrenaline",
		Key = "Adrenaline",
		Description = ::UPD.getDescription({
			Fluff = "感受肾上腺素在血管中奔涌！",
			Effects = [{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+adrenaline_skill]技能，该技能能让你在下一[轮|Concept.Round]中最先行动，在敌人行动之前进行[回合|Concept.Turn]。",
					"在[$ $|Skill+adrenaline_effect]的效果下，你不会受到[临时创伤|Concept.InjuryTemporary]，也不会被其影响。"
				]
			}]
		})
	},
	{
		ID = "perk.anticipation",
		Key = "Anticipation",
		Description = ::UPD.getDescription({
			Fluff = "我都看见了！",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"受远程武器攻击时，每距离攻击者1格远，获得" + ::MSU.Text.colorPositive("1 + 10%") + "你[基础|Concept.BaseAttribute][远程防御|Concept.RangeDefense]的[远程防御|Concept.RangeDefense]加值。至少" + ::MSU.Text.colorPositive("+10") + "[远程防御|Concept.RangeDefense]。"
				]
			}]
		})
	},
	{
		ID = "perk.bags_and_belts",
		Key = "BagsAndBelts",
		Description = ::UPD.getDescription({
			Fluff = "有备无患。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"解锁两个额外的[背包槽位|Concept.BagSlots]。",
					"放在[背包槽位|Concept.BagSlots]里的物品不再对[疲劳值上限|Concept.MaximumFatigue]造成惩罚，双手武器除外。"
				]
			}]
		})
	},
	{
		ID = "perk.taunt",
		Key = "Taunt",
		Description = ::UPD.getDescription({
			Fluff = "你只配日马！",
			Effects = [{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+taunt]技能，该技能会使目标对手采取进攻行动而不是防御行动，攻击该角色而非更脆弱的其他角色。",
					"对接邻的目标使用时，降低其[近战防御|Concept.MeleeDefense]和[远程防御|Concept.RangeDefense]，降低值为使用者[决心|Concept.Bravery]的" + ::MSU.Text.colorPositive("20%") + "。"
				]
			}]
		})
	},
	{
		ID = "perk.recover",
		Key = "Recover",
		Description = ::UPD.getDescription({
			Fluff = "稍作歇息重返战斗，丢掉脑袋永远退出。",
			Effects = [{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+recover_skill]技能，该技能允许角色通过休息一[回合|Concept.Turn]，减少累积[疲劳值|Concept.Fatigue]。"
				]
			}]
		})
	},
	{
		ID = "perk.underdog",
		Key = "Underdog",
		Description = ::UPD.getDescription({
			Fluff = "我已经习惯了。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"陷入[围攻|Concept.Surrounding]带来的防御减益不再对该角色生效。",
					"若攻击方有[$ $|Perk+perk_backstabber]特技，则抵消特技效果，常规的[围攻|Concept.Surrounding]防御减益生效。"
				]
			}]
		})
	},
	{
		ID = "perk.coup_de_grace",
		Key = "CoupDeGrace",
		Description = ::UPD.getDescription({
			Fluff = "“手起头落！”",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"对身负[创伤|Concept.Injury]或陷入[沉睡|Skill+sleeping_effect]、[$ $|Skill+stunned_effect]、[$ $|Skill+net_effect]、[$ $|Skill+web_effect]或[$ $|Skill+rooted_effect]的敌人造成的伤害提高" + ::MSU.Text.colorPositive("20%") + "。"
				]
			}]
		})
	},
	{
		ID = "perk.crippling_strikes",
		Key = "CripplingStrikes",
		Description = ::UPD.getDescription({
			Fluff = "致残你的敌人！",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"近战及远程攻击造成[创伤|Concept.Injury]的[阈值|Concept.InjuryThreshold]降低" + ::MSU.Text.colorNegative("33%") + "。"
				]
			}]
		})
	},
	{
		ID = "perk.duelist",
		Key = "Duelist",
		Description = ::UPD.getDescription({
			Fluff = "人兵合一，直取空门！",
			Requirement = "主要近战攻击技能基础[行动点数|Concept.ActionPoints]消耗不高于4的武器",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"额外伤害穿甲率，单手武器" + ::MSU.Text.colorPositive("25%") + "，单手武器持盾" + ::MSU.Text.colorPositive("35%") + "，双手武器" + ::MSU.Text.colorPositive("15%") + "。",
					"盾牌能在攻击时抵消目标的[触及优势|Concept.ReachAdvantage]。"
				]
			}],
			Footer = ::MSU.Text.colorNegative("该特技仅适用于攻击范围为1的非AOE近战攻击，[$ $|Skill+lunge_skill]除外。")
		})
	},
	{
		ID = "perk.hold_out",
		Key = "HoldOut",
		Description = ::UPD.getDescription({
			Fluff = "挺住!",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"所有有限时间的负面[状态效果|Concept.StatusEffect]（如[$ $|Skill+disarmed_effect]， [$ $|Skill+charmed_effect]等）的持续时间减少到" + ::MSU.Text.colorPositive(1) + "[回合|Concept.Turn]。",
					"随回合而减弱的效果[状态效果|Concept.StatusEffect]（如[$ $|Skill+goblin_poison_effect]）一开始就处于其最弱的状态。",
					"[$ $|Skill+bleeding_effect]的效果" + ::MSU.Text.colorPositive("减半") + "。"
				]
			}]
		})
	},
	{
		ID = "perk.indomitable",
		Key = "Indomitable",
		Description = ::UPD.getDescription({
			Fluff = "“山不可移，亦不可倒！”",
			Effects = [
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+indomitable]技能，该技能能减少受到的伤害，以及对[$ $|Skill+stunned_effect]、击退或钩拽的免疫。"
					]
				}
			]
		})
	},
	{
		ID = "perk.lone_wolf",
		Key = "LoneWolf",
		Description = ::UPD.getDescription({
			Fluff = "我最好单独行动。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"若没有相邻同阵营友军，两格内的同阵营友军也不超过1人，[近战技能|Concept.MeleeSkill]、[远程技能|Concept.RangeSkill]、[近战防御|Concept.MeleeDefense]、[远程防御|Concept.RangeDefense]及[决心|Concept.Bravery]均提高" + ::MSU.Text.colorPositive("15%") + "。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.axe",
		Key = "SpecAxe",
		Description = ::UPD.getDescription({
			Fluff = "精通斧头，摧毁盾牌。",
			Requirement = "斧",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
						"[$ $|Skill+round_swing]的命中率提高" + ::MSU.Text.colorPositive("+5%") + "。"
						"使用[$ $|Item+longaxe]和[$ $|Item+rf_poleaxe]攻击接邻敌人不再有命中率惩罚。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_bearded_blade_skill]技能，该技能能使你在攻击或对手攻击落空时缴械对手。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_hook_shield_skill]技能，该技能允许你降低对手盾牌的效果。"
					]
				}
			]
		})
	},
	{
		ID = "perk.mastery.bow",
		Key = "SpecBow",
		Description = ::UPD.getDescription({
			Fluff = "精通射箭，向对手倾泻箭雨。",
			Requirement = "弓",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
						"视野范围和使用弓时的最大射程" + ::MSU.Text.colorPositive("+1") + "。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_arrow_to_the_knee_skill]技能，削弱你对手在战场上移动的能力。"
					]
				}
			]
		})
	},
	{
		ID = "perk.mastery.cleaver",
		Key = "SpecCleaver",
		Description = ::UPD.getDescription({
			Fluff = "精通砍刀，造成可怕伤口。",
			Requirement = "砍刀",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"获得[$ $|Perk+perk_rf_bloodlust]特技。",
					"砍刀攻击多施加一层[$ $|Skill+bleeding_effect]效果。",
					"[$ $|Skill+disarm_skill]的命中率惩罚减半。",
					"[$ $|Skill+rf_gouge_skill]造成[创伤|Concept.InjuryTemporary]的[阈值|Concept.InjuryThreshold]降低" + ::MSU.Text.colorNegative("50%") + "。",
					"[$ $|Item+rf_voulge]攻击接邻敌人不再有命中率惩罚。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.crossbow",
		Key = "SpecCrossbow",
		Description = ::UPD.getDescription({
			Fluff = "精通弩和火器，一发破的。",
			Requirement = "弩",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
						"[$ $|Item+heavy_crossbow]现在同普通弩一样，只需" + ::MSU.Text.colorNegative("4") + "点[行动点数|Concept.ActionPoints]就能完成[$ $|Skill+reload_bolt]。使你可以在一回合中完成射击、装填和移动。",
						"[$ $|Item+handgonne]现仅需" + ::MSU.Text.colorNegative("6") + "点[行动点数|Concept.ActionPoints]就能完成[$ $|Skill+reload_bolt]。使你可以每回合射击一次。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_take_aim_skill]技能，使你能用[$ $|Item+crossbow]锁定障碍后面的对手或使用[$ $|Item+handgonne]打击更多目标"
					]
				},

			]
		})
	},
	{
		ID = "perk.mastery.dagger",
		Key = "SpecDagger",
		Description = ::UPD.getDescription({
			Fluff = "精通匕首，迅捷而致命。",
			Requirement = "匕首",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"使用匕首攻击本[轮|Concept.Round]行动顺序在你之后的对手时，无视目标所有[触及优势|Concept.ReachAdvantage]。",
					"[$ $|Skill+stab]、[$ $|Skill+puncture]和[$ $|Skill+deathblow_skill]消耗的[行动点数|Concept.ActionPoints]减少1，使你每回合可以多攻击一次。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.flail",
		Key = "SpecFlail",
		Description = ::UPD.getDescription({
			Fluff = "精通链枷，绕过对手的盾牌。",
			Requirement = "链枷",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"[$ $|Skill+lash_skill]和[$ $|Skill+hail_skill]无视除[$ $|Skill+shieldwall_effect]效果外的盾牌的防御加成。",
					"获得[$ $|Perk+perk_rf_from_all_sides]特技。",
					"[$ $|Skill+pound]命中头部时穿甲提升" + ::MSU.Text.colorPositive("+10%") + "。",
					"[$ $|Skill+thresh]命中率提高" + ::MSU.Text.colorPositive("+5%") + "。",
					"使用长链枷攻击近身敌人不再有命中率惩罚。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.hammer",
		Key = "SpecHammer",
		Description = ::UPD.getDescription({
			Fluff = "精通锤子，对付重甲对手。",
			Requirement = "锤",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
						"[$ $|Skill+crush_armor]和[$ $|Skill+demolish_armor_skill]造成的护甲伤害提高" + ::MSU.Text.colorPositive("33%") + "并会对对手施加[$ $|Skill+rf_dented_armor_effect]效果。",
						"[$ $|Skill+shatter_skill]的命中率提高" + ::MSU.Text.colorPositive("+5%") + "。",
						"使用[$ $|Item+polehammer]攻击近身敌人不再有命中率惩罚。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"使用双手锤时，获得[$ $|Skill+rf_pummel_skill]技能。"
					]
				}
			]
		})
	},
	{
		ID = "perk.mastery.mace",
		Key = "SpecMace",
		Description = ::UPD.getDescription({
			Fluff = "精通骨朵，不论护甲一通暴打。",
			Requirement = "骨朵",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"获得[$ $|Perk+perk_rf_bear_down]特技。"
					"若目标不免疫，[$ $|Skill+knock_out]、[$ $|Skill+knock_over_skill]和[$ $|Skill+strike_down_skill]技能[击晕|Skill+stunned_effect]对手的概率提升为" + ::MSU.Text.colorPositive("100%") + "。",
					"使用长棒攻击近身敌人不再有命中率惩罚。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.polearm",
		Key = "SpecPolearm",
		Description = ::UPD.getDescription({
			Fluff = "精通长柄，拒敌于外。",
			Requirement = "长柄武器",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"获得[$ $|Perk+perk_rf_bolster]特技。"
					"所有攻击范围为2格、[行动点数|Concept.ActionPoints]消耗为" + ::MSU.Text.colorNegative("6") + "点的双手武器技能[行动点数|Concept.ActionPoints]消耗减少至" + ::MSU.Text.colorNegative("5") + "点。",
					"使用长柄武器攻击近身敌人不再有命中率惩罚。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.spear",
		Key = "SpecSpear",
		Description = ::UPD.getDescription({
			Fluff = "精通长矛，拒敌于外。",
			Requirement = "矛",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"[$ $|Skill+spearwall]不再因有敌人突破而立即失效。而是可以继续使用，通过免费攻击阻止敌人进入[控制区|Concept.ZoneOfControl]。",
					"[回合|Concept.Turn]开始时，若你装备有矛，你的第一次矛穿刺攻击将" + ::MSU.Text.colorPositive("不消耗") + "[行动点数|Concept.ActionPoints]，且积累的[疲劳|Concept.Fatigue]降低" + ::MSU.Text.colorPositive("50%") + "。该效果会在你装备双手矛移动或装备单手矛移动超过1格后消失。",
					"[$ $|Item+spetum]和[$ $|Item+warfork]攻击近身敌人不再有命中率惩罚。"
				]
			}]
		})
	},
	{
		ID = "perk.mastery.sword",
		Key = "SpecSword",
		Description = ::UPD.getDescription({
			Fluff = "精通剑术，将对手失误化为自身优势。",
			Requirement = "剑",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
						"[$ $|Skill+riposte]不再有命中率惩罚。",
						"[$ $|Skill+gash_skill]造成[创伤|Concept.InjuryTemporary]的[阈值|Concept.InjuryThreshold]降低" + ::MSU.Text.colorNegative("50%") + "。",
						"[$ $|Skill+split]和[$ $|Skill+swing]不再有命中率惩罚，且命中率提高" + ::MSU.Text.colorPositive("+5%") + "。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_passing_step_skill]技能，该技能可使你在攻击成功之后立即无视[控制区|Concept.ZoneOfControl]移动1格，消耗的[行动点数|Concept.ActionPoints]减少，但[疲劳|Concept.Fatigue]积累" + ::MSU.Text.colorNegative("+2") + "。",
						"目标地格必须接邻一名敌人。",
						"装备双手剑或双手握持的单手剑进行挥砍攻击时才能使用。"
					]
				}
			]
		})
	},
	{
		ID = "perk.mastery.throwing",
		Key = "SpecThrowing",
		Description = ::UPD.getDescription({
			Fluff = "精通投掷，先下手为强。",
			Requirement = "投掷武器",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
					"攻击2格远的目标时，伤害提高" + ::MSU.Text.colorPositive("30%") + "，攻击3格远的目标时，伤害提高" + ::MSU.Text.colorPositive("20%") + "。",
					"远程投掷命中会对目标施加特定减益。穿刺攻击有" + ::MSU.Text.colorPositive("50%") + "概率施加[$ $|Skill+rf_arrow_to_the_knee_debuff_effect]。挥砍攻击总会施加[$ $|Skill+overwhelmed_effect]。钝击攻击有" + ::MSU.Text.colorPositive("50%") + "概率施加[$ $|Skill+staggered_effect]，如目标已经[$ $|Skill+staggered_effect]，则会" + ::MSU.Text.colorPositive("100%") + "使目标[$ $|Skill+stunned_effect]。"
				]
			}]
		})
	},
	{
		ID = "perk.student",
		Key = "Student",
		Description = ::UPD.getDescription({
			Fluff = "世上无难事，只怕有心人。",
			Effects = [{
				Type = ::UPD.EffectType.OneTimeEffect,
				Description = [
					"该角色升到十一级时，该特技失效并获得一个额外特技点。",
					"游玩“猎奴者”起源，你的负债者会在升到七级时返还特技点。"
				]
			},
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"战斗中获得的经验" + ::MSU.Text.colorPositive("20%") + "。"
				]
			}],
			Footer = ::MSU.Text.colorNegative("该特技不能遗忘。")	// This line is new, rest is the same
		})
	},
	{
		ID = "perk.gifted",
		Key = "Gifted",
		Description = ::UPD.getDescription({
			Fluff = "有了天赋，佣兵生活就会轻松许多。",
			Effects = [{
				Type = ::UPD.EffectType.OneTimeEffect,
				Description = [
					"该角色立即获得一次属性升级，数值取掷骰上限，不考虑天赋加成。"
				]
			}],
			Footer = ::MSU.Text.colorNegative("该特技不能遗忘。")	// This line is new, rest is the same
		})
	},
	{
		ID = "perk.nimble",
		Key = "Nimble",
		Description = ::UPD.getDescription({
			Fluff = "轻甲专精！通过灵活闪避和偏转攻击，避免受到直接攻击。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"受到的[生命值|Concept.Hitpoints]伤害减少" + ::MSU.Text.colorPositive("50%") + "，护甲伤害减少" + ::MSU.Text.colorPositive("25%") + "。",
					"盔甲和头盔的[疲劳值上限|Concept.MaximumFatigue]减益超过15点，且超过[基础|Concept.BaseAttribute][疲劳值|Concept.Fatigue]的15%时（包括[特性|Concept.Trait]和[永久创伤|Concept.InjuryPermanent]的影响），该增益的效果开始指数下降。",
					"不影响精神攻击和状态效果的伤害，但可以帮助避免受到这些效果。",
					"攻击具有[触及劣势|Concept.ReachAdvantage]的目标时，若你的[主动值|Concept.Initiative]高于对手，劣势减" + ::MSU.Text.colorPositive(1) + "。"
					"[$ $|Perk+perk_brawny]不影响本特技。",
					"拥有[$ $|Perk+perk_rf_poise]或[$ $|Perk+perk_battle_forged]后不能学习。"

				]
			}]
		})
	},
	{
		ID = "perk.overwhelm",
		Key = "Overwhelm",
		Description = ::UPD.getDescription({
			Fluff = "利用你的高[主动|Concept.Initiative]，用攻击压制敌人的攻击！",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"无论命中与否，每次攻击都会对本轮中后行动的敌人施加[$ $|Skill+overwhelmed_effect]效果。该效果会降低对手[近战技能|Concept.MeleeSkill]和[远程技能|Concept.RangeSkill]各" + ::MSU.Text.colorNegative("-10%") + "，持续1回合。",
					"该效果在每次攻击中都会叠加，最多7层，可以通过一次攻击同时施加给多个目标。"
				]
			}]
		})
	},
	{
		ID = "perk.pathfinder",
		Key = "Pathfinder",
		Description = ::UPD.getDescription({
			Fluff = "学会在复杂地形上移动。",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"所有地形上的每格移动[行动点数|Concept.ActionPoints]消耗减少" + ::MSU.Text.colorPositive("1") + "，最低不低于2，[疲劳值|Concept.Fatigue]积累减半。",
						"高度变化不再消耗额外的[行动点数|Concept.ActionPoints]。"
					]
				}
			]
		})
	},
	{
		ID = "perk.quick_hands",
		Key = "QuickHands",
		Description = ::UPD.getDescription({
			Fluff = "西部最快的手。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"战斗中，每[回合|Concept.Turn]第一次替换物品视为免费动作，不需要[行动点数|Concept.ActionPoints]。",
					"切换盾牌或在双手武器间切换时无效。",
					"不与其他免费切换物品的技能叠加。"
				]
			}]
		})
	},
	{
		ID = "perk.shield_expert",
		Key = "ShieldExpert",
		Description = ::UPD.getDescription({
			Fluff = "学会偏转攻击，而非正面硬扛。",
			Requirement = "盾牌",
			Effects = [
				{
					Type = ::UPD.EffectType.Passive,
					Description = [
						"盾牌防御加成提高" + ::MSU.Text.colorPositive("25%") + "。也适用于[$ $|Skill+shieldwall]技能提供的额外防御加成。",
						"[疲劳|Concept.Fatigue]积满时，盾牌防御下降到值从" + ::MSU.Text.colorNegative("50%") + "减少到" + ::MSU.Text.colorNegative("25%") + "。",
						"未命中的攻击不再使你积累[疲劳|Concept.Fatigue]。"
					]
				},
				{
					Type = ::UPD.EffectType.Active,
					Description = [
						"解锁[$ $|Skill+rf_cover_ally_skill]技能，该技能能使你选择一名盟友，使其能在自己[回合|Concept.Turn]中无视[控制区|Concept.ZoneOfControl]移动1格，并将其在下一[轮|Concept.Round]中的行动顺序提前。"
					]
				}
			]
		})
	},
	{
		ID = "perk.steel_brow",
		Key = "SteelBrow",
		Description = ::UPD.getDescription({
			Fluff = "“我能受得住！”",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"击中该角色头部的攻击不再造成暴击伤害，也有赖于此，显著降低了受头部[创伤|Concept.Injury]削弱的风险。"
				]
			}]
		})
	},
	{
		ID = "perk.nine_lives",
		Key = "NineLives",
		Description = ::UPD.getDescription({
			Fluff = "好奇就算能害死猫，也得花上一段时间。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"每场战斗限一次，遭受致命伤害时，你会以少量的[生命值|Concept.Hitpoints]存活下来，并治愈所有的持续伤害效果（如[$ $|Skill+bleeding_effect]、[$ $|Skill+spider_poison_effect]等）。",
					"一旦效果触发，直到下[回合|Concept.Turn]开始前，获得[$ $|Skill+nine_lives_effect]效果。"
				]
			}]
		})
	},
	{
		ID = "perk.brawny",
		Key = "Brawny",
		Description = ::UPD.getDescription({
			Fluff = "穿甲就像龟穿壳。",
			Effects = [{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"穿着盔甲和头盔带来的疲劳和主动值惩罚降低" + ::MSU.Text.colorNegative("30%") + "。"
				]
			}]
		})
	}
];

::MSU.Table.merge(::Const.Strings.PerkDescription, {
	RF_Angler = ::UPD.getDescription({
		Fluff = "撒网的要领是完美地兜住所有目标。",
		Requirement = "投网",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"你[$ $|Skill+throw_net]的距离提高1格，最多为3格。",
					"被你[网|Skill+net_effect]在两格内的敌人要多花费" + ::MSU.Text.colorNegative("50%") + "的[行动点数|Concept.ActionPoints]才能[挣脱|Skill+break_free_skill]。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_net_pull_skill]技能，使你可以[网住|Skill+net_effect]并拖动目标。"
				]
			}
		]
	}),
	RF_BattleFervor = ::UPD.getDescription({
		Fluff = "这就是我们的使命！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每[回合|Concept.Turn]一次，若你处在[自信|Concept.Morale]士气，进行一次[士气检定|Concept.Morale]，若成功，获得一层效果，最多叠加4层。每有一层，[决心值|Concept.Bravery]、[近战技能|Concept.MeleeSkill]、[远程技能|Concept.RangeSkill]、[近战防御|Concept.MeleeDefense]和[远程防御|Concept.RangeDefense]各提升" + ::MSU.Text.colorPositive("5%") + "。",
				"若某个[回合|Concept.Turn]结束前没有进行过攻击，失去" + ::MSU.Text.colorNegative(1) + "层效果。",
				"失去自信[士气|Concept.Morale]时，立即失去所有层数。"
			]
		}]
	}),
	RF_BackToBasics = ::UPD.getDescription({
		Fluff = "练武不练功，到头一场空！",
		Effects = [{
			Type = ::UPD.EffectType.OneTimeEffect,
			Description = [
				"获得2点特技点。",
				"你的[特技层级|Concept.PerkTier]降到" + ::MSU.Text.colorNegative(2) + "。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("该特技不能遗忘。")
	}),
	RF_Skirmisher = ::UPD.getDescription({
		Fluff = "通过平衡护甲和机动性来提高速度和耐受能力。",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"头身护甲的[主动值|Concept.Initiative]减益降低" + ::MSU.Text.colorPositive("30%") + "。",
				"无论何时，你的[主动值|Concept.Initiative]受到累积[疲劳值|Concept.Fatigue]的惩罚降至" + ::MSU.Text.colorPositive("50%") + "，而非100%。",
				"与[$ $|Perk+perk_relentless]特技[乘法叠加|Concept.StackMultiplicatively]。"
			]
		}]
	}),
	BattleFlow = ::UPD.getDescription({
		Fluff = "下一个！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每[回合|Concept.Turn]一次，杀敌时，将当前[疲劳|Concept.Fatigue]降低[基础|Concept.BaseAttribute][疲劳值上限|Concept.MaximumFatigue]的" + ::MSU.Text.colorPositive("10%") + "。"
			]
		}]
	}),
	RF_BearDown = ::UPD.getDescription({
		Fluff = "“先是猛锤一下，然后人头拿下！”",
		Requirement = "骨朵",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击[$ $|Skill+rf_rattled_effect]、[$ $|Skill+stunned_effect]、[$ $|Skill+dazed_effect]、[$ $|Skill+net_effect]、[$ $|Skill+sleeping_effect]、[$ $|Skill+staggered_effect]、[$ $|Skill+web_effect]或[$ $|Skill+rooted_effect]的目标时，命中头部概率提高" + ::MSU.Text.colorPositive("+15%") + "，[创伤|Concept.InjuryTemporary][阈值|Concept.InjuryThreshold]降低" + ::MSU.Text.colorPositive("33%") + "。"
			]
		}]
	}),
	RF_BestialVigor = ::UPD.getDescription({
		Fluff = "释放心中的野兽！",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_bestial_vigor_skill]技能，能使你在战斗中降低累积[疲劳|Concept.Fatigue]，获得[行动点数|Concept.ActionPoints]。"
			]
		}]
	}),
	RF_BetweenTheEyes = ::UPD.getDescription({
		Fluff = "热刀切黄油！",
		Requirement = "近战攻击",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_between_the_eyes_skill]技能。"
			]
		}]
	}),
	RF_BetweenTheRibs = ::UPD.getDescription({
		Fluff = "在敌人分心时发动攻击，让该角色更容易瞄准脆弱部位！",
		Requirement = "匕首穿刺攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击[被围攻|Concept.Surrounding]的目标时，每有一名围攻角色，造成的伤害提高" + ::MSU.Text.colorPositive("10%") + "，且有" + ::MSU.Text.colorPositive("+10%") + "的穿甲率。"
			]
		}]
	}),
	RF_Blitzkrieg = ::UPD.getDescription({
		Fluff = "马上见分晓！",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_blitzkrieg_skill]技能，该技能会使你和其他战团成员获得[$ $|Skill+adrenaline_effect]效果。"
			]
		}]
	}),
	RF_Bloodlust = ::UPD.getDescription({
		Fluff = "腥风血雨让你精神一振，宾至如归！",
		Requirement = "砍刀",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"造成[残杀|Concept.Fatality]后，获得" + ::MSU.Text.colorPositive("2") + "层嗜血，最多叠加2层。",
				"每有一层，[决心|Concept.Bravery]、[主动值|Concept.Initiative]和[疲劳恢复|Concept.FatigueRecovery]速率提升" + ::MSU.Text.colorPositive("15%") + "各层效果[加算|Concept.StackAdditively]。",
				"每[回合|Concept.Turn]开始时，失去" + ::MSU.Text.colorNegative("1") + "层。"
			]
		}]
	}),
	RF_Command = ::UPD.getDescription({
		Fluff = "“做好你该做的！”",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_command_skill]技能，让你能提前盟友的回合排序。"
			]
		}]
	}),
	RF_CalculatedStrikes = ::UPD.getDescription({
		Fluff = "别着急，结结实实的来上一下！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"对本[轮|Concept.Round]中尚未开始[回合|Concept.Turn]的目标造成的伤害提高" + ::MSU.Text.colorPositive("20%") + "。"
				"[主动值|Concept.Initiative]降低" + ::MSU.Text.colorNegative("20%") + "。"
			]
		}]
	}),
	RF_CheapTrick = ::UPD.getDescription({
		Fluff = "不讲武德？这叫兵不厌诈！",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_cheap_trick_skill]技能，使你能以部分伤害为代价提高命中率。"
			]
		}]
	}),
	RF_DeathDealer = ::UPD.getDescription({
		Fluff = "就像镰刀前的麦子！",
		Requirement = "近战[范围|Concept.AOE]攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"近战[范围|Concept.AOE]攻击命中率提高" + ::MSU.Text.colorPositive("+10%") + "，造成的伤害提高" + ::MSU.Text.colorPositive("10%") + "。"
			]
		}]
	}),
	RF_Bolster = ::UPD.getDescription({
		Fluff = "有了你的支持，战友们充满信心！",
		Requirement = "6点或以上[触及距离|Concept.Reach]的武器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"没有[陷入近战|Concept.ZoneOfControl]时，无论命中与否，你的攻击触发所有未[溃逃|Concept.Morale]接邻队友的正面[士气检定|Concept.Morale]。"
			]
		}]
	}),
	RF_BoneBreaker = ::UPD.getDescription({
		Fluff = "啪嗒，嘎吱，碎了。真是动听！",
		Requirement = "骨朵钝击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"当攻击造成的[生命值|Concept.Hitpoints]伤害不少于" + ::MSU.Text.colorNegative(5) + "点时，若该攻击施加了有效的[状态效果|Concept.StatusEffect]，或攻击的目标已有这些[状态效果|Concept.StatusEffect]时，有概率对目标施加[创伤|Concept.Injury]。对于双手骨朵，该概率为" + ::MSU.Text.colorPositive("100%") + "，对于单手骨朵则为" + ::MSU.Text.colorPositive("50%") + "。",
				"如果造成的伤害本来就足以施加[创伤|Concept.Injury]，额外施加一个[创伤|Concept.Injury]。",
				"单回合中，对同一个目标只生效一次。",
				"有效状态效果包括：[$ $|Skill+stunned_effect]、[$ $|Skill+net_effect]、[$ $|Skill+web_effect]、[$ $|Skill+rooted_effect]和[$ $|Skill+sleeping_effect]。"
			]
		}]
	}),
	RF_Bully = ::UPD.getDescription({
		Fluff = "你说停？",
		Requirement = "近战攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击[士气|Concept.Morale]低于你的角色时，[士气|Concept.Morale]每差一级，造成的伤害提高" + ::MSU.Text.colorPositive("10%") + "。"
			]
		}]
	}),
	RF_Bulwark = ::UPD.getDescription({
		Fluff = "“有了合身铁甲，还有什么好怕！”",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"[士气检定|Concept.Morale]中，获得等于当前头身护甲总值" + ::MSU.Text.colorPositive("5%") + "的[决心值|Concept.Bravery]加值。在负面[士气检定|Concept.Morale]中，加值翻倍。",
				"对精神攻击无效。"
			]
		}]
	}),
	RF_Finesse = ::UPD.getDescription({
		Fluff = "多年的实战训练让你洞悉了战场上如何行动最为有效。",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"技能[疲劳|Concept.Fatigue]积累降低" + ::MSU.Text.colorPositive("20%") + "。"
			]
		}]
	}),
	RF_Centurion = ::UPD.getDescription({
		Fluff = "再快点！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使最远6格内的友军骷髅触发[$ $|Skill+rf_centurion_command_effect]效果。"
			]
		}]
	}),
	RF_Combo = ::UPD.getDescription({
		Fluff = "还是那招，一，二！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使用任何消耗[行动点数|Concept.ActionPoints]技能会让所有技能消耗的[行动点数|Concept.ActionPoints]减少" + ::MSU.Text.colorPositive("1") + "，最多减少到3。",
				"效果会在使用技能、[等待|Concept.Wait]或结束[回合|Concept.Turn]时失效。"
			]
		}]
	}),
	RF_ConcussiveStrikes = ::UPD.getDescription({
		Fluff = "骨朵敲了头，睡眠不发愁！",
		Requirement = "骨朵钝击"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使用单手骨朵命中头部时，若目标已经陷入[$ $|Skill+dazed_effect]或该攻击本身会施加[$ $|Skill+dazed_effect]，[击晕|Skill+stunned_effect]目标1[回合|Concept.Turn]。否则，施加1[回合|Concept.Turn]的[$ $|Skill+dazed_effect]效果。",
				"使用双手骨朵命中目标头部会[击晕|Skill+stunned_effect]目标1[回合|Concept.Turn]."
			]
		}]
	}),
	RF_Decanus = ::UPD.getDescription({
		Fluff = "列队接战！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使最远4格内的友军骷髅触发[十夫长之命|Skill+rf_decanus_command_effect]效果。"
			]
		}]
	}),
	RF_Decisive = ::UPD.getDescription({
		Fluff = "没有时间再等了！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每次不经[等待|Concept.Wait]便结束[回合|Concept.Turn]时，叠加一层效果，最多3层。",
				"如有至少1层，[决心|Concept.Bravery]和[主动值|Concept.Initiative]各提高" + ::MSU.Text.colorPositive("15%") + "。",
				"如有至少2层，技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("15%") + "。",
				"如有至少3层，造成的伤害提高" + ::MSU.Text.colorPositive("15%") + "。",
				"使用[等待时|Concept.Wait]失去所有层数。"
			]
		}]
	}),
	RF_DeepCuts = ::UPD.getDescription({
		Fluff = "你知道怎样使用磨刀石才能让你的刃口锋利无比！",
		Requirement = "挥砍攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"在你的[回合|Concept.Turn]当中，成功攻击目标1次后，后续所有攻击造成[创伤|Concept.InjuryTemporary]的[阈值|Concept.InjuryThreshold]降低" + ::MSU.Text.colorNegative("33%") + "。并会对目标施加[$ $|Skill+bleeding_effect]效果。若任意一次攻击造成了[创伤|Concept.InjuryTemporary]，施加额外的[$ $|Skill+bleeding_effect]效果。",
				"该效果会在更改目标、移动、切换物品、等待、结束[回合|Concept.Turn]或使用挥砍攻击以外的技能时失效。"
			]
		}]
	}),
	RF_DeepImpact = ::UPD.getDescription({
		Fluff = "“高速挥舞，重击摧骨！”",
		Requirement = "锤钝击",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁能削弱目标的[$ $|Skill+rf_deep_impact_skill]技能。"
			]
		}]
	}),
	RF_DentArmor = ::UPD.getDescription({
		Fluff = "“不能走路，何谈战斗。”",
		Requirement = "钝击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"成功的攻击有" + ::MSU.Text.colorPositive("66%") + "概率对目标施加[$ $|Skill+rf_dented_armor_effect]效果。"
			]
		}]
	}),
	RF_DiscoveredTalent = ::UPD.getDescription({
		Fluff = "不知究竟是怎么回事，你突然对所有事都在行了！",
		Effects = [{
			Type = ::UPD.EffectType.OneTimeEffect,
			Description = [
				"每次花费升级点数时，使一项[天赋|Concept.Talent]星数不足3点的属性随机获得" + ::MSU.Text.colorPositive(1) + "到" + ::MSU.Text.colorPositive(3) + "点星星。",
				"每个属性只能触发一次，不能使[天赋|Concept.Talent]星数超过3。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("花费过任何特技点后便无法获得。该特技不能遗忘。")
	}),
	RF_Dismantle = ::UPD.getDescription({
		Fluff = "穿着盔甲，照样扯烂！",
		Requirement = "斧挥砍攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每次成功攻击都有概率施加[$ $|Skill+rf_dismantled_effect]效果，使目标在同一身体部位受到的穿甲伤害提高" + ::MSU.Text.colorNegative("+20%") + "，效果可叠加，持续整场战斗。",
				"概率为造成的护甲伤害和命中的身体部位剩余护甲值的比值。"
			]
		}]
	}),
	RF_Dismemberment = ::UPD.getDescription({
		Fluff = "我为刀俎！",
		Requirement = "斧挥砍攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每次通过攻击施加[创伤|Concept.InjuryTemporary]时，如果你达到了要求[阈值|Concept.InjuryThreshold]最低的创伤的阈值，转而施加要求[阈值|Concept.InjuryThreshold]最高的创伤。",
				"这次[创伤|Concept.InjuryTemporary]至少多触发一次[士气检定|Concept.Morale]最多触发" + ::MSU.Text.colorNegative(3) + "次。造成的[生命值|Concept.Hitpoints]伤害每超过剩余[生命值|Concept.Hitpoints]的" + ::MSU.Text.colorPositive("33%") + "，就会多触发一次。"
			]
		}]
	}),
	RF_DoubleStrike = ::UPD.getDescription({
		Fluff = "看好了，还有一下！",
		Requirement = "近战攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"成功攻击会使你下次攻击造成的伤害提高" + ::MSU.Text.colorPositive("20%") + "。",
				"会在移动、切换物品、使用单体攻击以外技能、攻击未命中、[等待|Concept.Wait]或结束[回合|Concept.Turn]时失效。"
			]
		}]
	}),
	RF_DynamicDuo = ::UPD.getDescription({
		Fluff = "你已经知道，在同伴掩护下一起战斗才是最好。",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"允许你选择战团中的一名成员作为搭档。除非一方死亡或离开战团，搭档关系保留。你和搭档身边都没有友军时双方会获得以下加成。",
					"对攻击你搭档的敌人发起攻击时，[近战技能|Concept.MeleeSkill]" + ::MSU.Text.colorPositive("+10") + "，受被你搭档攻击过的敌人攻击时，[近战防御|Concept.MeleeDefense]" + ::MSU.Text.colorPositive("+10") + "，持续1[回合。|Concept.Turn]",
					"一名搭档的近战[范围|Concept.AOE]攻击命中另一名搭档的概率不会超过" + ::MSU.Text.colorPositive(::Const.Combat.MV_HitChanceMin + "%") + "，且造成的伤害降低" + ::MSU.Text.colorPositive("50%") + "。",
					"搭档不需要学习此[特技|Concept.Perk]便能获得增益效果。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"获得[$ $|Skill+rf_dynamic_duo_shuffle_skill]技能，每[回合|Concept.Turn]中，该技能使你可以和搭档换位1次。并让对方置于[回合|Concept.Turn]排序的下一位，在你之后立即行动。"
				]
			}
		]
	}),
	RF_EnGarde = ::UPD.getDescription({
		Fluff = "你的剑法已练得炉火纯青，攻守兼备！",
		Requirement = "剑",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"副手物品重量低于" + ::MSU.Text.colorNegative("10") + "点时，南方剑的双手持握效果不会失效，且进行免费攻击时，使用[$ $|Skill+gash_skill]而非[$ $|Skill+slash]技能。"
				"如果武器拥有[还击|Skill+riposte]，[回合|Concept.Turn]结束时会免费使用[还击|Skill+riposte]。如果武器没有[还击|Skill+riposte]且为双手武器，则获得[迎击|Perk+perk_rf_rebuke]，持续1[回合|Concept.Turn]。对未命中攻击触发迎击的概率提高" + ::MSU.Text.colorPositive("+15%") + "。该[迎击|Perk+perk_rf_rebuke]触发的攻击不会积累[疲劳。|Concept.Fatigue]",
				"至少剩余" + ::MSU.Text.colorNegative(15) + "点[疲劳|Concept.Fatigue]才能触发该特技，但该特技不会消耗[行动点数|Concept.ActionPoints]或积累[疲劳|Concept.Fatigue]。"
			]
		}]
	}),
	RF_Entrenched = ::UPD.getDescription({
		Fluff = "你学会了结阵作战，坚信前后的战友会在你射击的时候保证你的安全！",
		Requirement = "远程武器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"身边有装备近战武器且并未[陷入近战|Concept.ZoneOfControl]的队友时，[远程技能|Concept.RangeSkill]、[远程防御|Concept.RangeDefense]和[决心|Concept.Bravery]各" + ::MSU.Text.colorPositive("+7") + "，只要你继续在装备近战武器且并未[陷入近战|Concept.ZoneOfControl]的队友身边开始回合，每[回合|Concept.Turn]再" + ::MSU.Text.colorPositive("+2") + "，最大叠加到" + ::MSU.Text.colorPositive("+15") + "。"
			]
		}]
	}),
	RF_ExploitOpening = ::UPD.getDescription({
		Fluff = "放低的盾牌，拖沓的刺击，假装被绊倒。都是你学会引诱对手做出致命决定的假动作！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击没能命中你的敌人时，你对他的下次攻击命中率" + ::MSU.Text.colorPositive("+10%") + "，或无视他的盾牌，取加成高的那一个，并且造成的伤害还能提高" + ::MSU.Text.colorPositive("20%") + "。效果会在你下次攻击、[等待|Concept.Wait]或结束[回合|Concept.Turn]后消失。"
			]
		}]
	}),
	RF_ExudeConfidence = ::UPD.getDescription({
		Fluff = "有你在战友身边，他们连山都能征服！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"你的[回合|Concept.Turn]开始时，如果[士气|Concept.Morale]等级不低于稳定，只要身边盟友的[士气等级|Concept.Morale]低于你，其[士气等级|Concept.Morale]提高" + ::MSU.Text.colorPositive(1) + "级。"
			]
		}]
	}),
	RF_FailedPotential = ::UPD.getDescription({
		Fluff = "该角色看起来很有前途，但由于运气不佳或干脆是缺乏天赋，他们并没有展现出你想象中的潜力。" + ::MSU.Text.colorNegative("该特技没有任何效果。"),
		Footer = ::MSU.Text.colorNegative("该特技不能遗忘。")
	}),
	RF_FamilyPride = ::UPD.getDescription({
		Fluff = "不荣耀，毋宁死！",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"总是以自信[士气|Concept.Morale]开始战斗。",
					"面对负面[士气检定|Concept.Morale]时，[决心|Concept.Bravery]提高" + ::MSU.Text.colorPositive("50%") + "。"
				]
			},
			{
				Type = ::UPD.EffectType.OneTimeEffect,
				Description = [
					"移除[$ $|Skill+insecure_trait]和[$ $|Skill+dastard_trait]特性。"
				]
			}
		]
	}),
	RF_Fencer = ::UPD.getDescription({
		Fluff = "用快剑战斗的大师。",
		Requirement = "刺剑",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"技能积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("20%") + "，命中率提高" + ::MSU.Text.colorPositive("+10%") + "。",
				"移除[$ $|Skill+rf_passing_step_skill] 的伤害类型要求。",
				"使用单手刺剑时，[$ $|Skill+rf_sword_thrust_skill]、[$ $|Skill+riposte]和[$ $|Skill+lunge_skill]的[行动点数|Concept.ActionPoints]消耗减少" + ::MSU.Text.colorPositive(1) + "点。",
				"使用双手刺剑时，[$ $|Skill+lunge_skill]的攻击范围增加" + ::MSU.Text.colorPositive(1) + "格。"
			]
		}]
	}),
	RF_FeralRage = ::UPD.getDescription({
		Fluff = "虎入羊群！",
		Requirement = "近战攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"战斗中会叠加狂怒。被命中积累1点，杀死目标积累3点，成功命中接邻目标积累2点。每[回合|Concept.Turn]开始时失去3点。",
				"每层狂怒提高[决心|Concept.Bravery]和[主动值|Concept.Initiative]" + ::MSU.Text.colorPositive("+2") + "点，近战伤害" + ::MSU.Text.colorPositive("2%") + "。每层使[近战防御|Concept.MeleeDefense]降低" + ::MSU.Text.colorNegative("-1") + "点，受到的伤害降低" + ::MSU.Text.colorPositive("2%") + "。最多降至70%。"
			]
		}]
	}),
	RF_FlailSpinner = ::UPD.getDescription({
		Fluff = "运用链枷惯性，快速再次攻击！",
		Requirement = "链枷",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"你的回合中，攻击有" + ::MSU.Text.colorPositive("50%") + "概率会施展一次同类型但伤害降低" + ::MSU.Text.colorNegative("50%") + "的免费额外攻击。"
			]
		}]
	}),
	RF_FlamingArrows = ::UPD.getDescription({
		Fluff = "烧光他们！",
		Requirement = "弓",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_flaming_arrows_skill]技能。"
			]
		}]
	}),
	RF_FollowUp = ::UPD.getDescription({
		Fluff = "“伙计打了你也打！”",
		Requirement = "近战攻击",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_follow_up_skill]技能，能使你在盟友[回合|Concept.Turn]中，攻击友军攻击的敌人！"
			]
		}]
	}),
	RF_FormidableApproach = ::UPD.getDescription({
		Fluff = "让他们敢靠近之前多想想！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"获得" + ::MSU.Text.colorPositive("+1") + "[触及距离|Concept.Reach]。",
				"对你[控制区|Concept.ZoneOfControl]内的敌人，每点你的[触及优势|Concept.ReachAdvantage]提供的加成" + ::MSU.Text.colorPositive("+1") + "，到他们命中你为止。被命中后效果消失，但会在[控制区|Concept.ZoneOfControl]被打破后重置。"
			]
		}]
	}),
	RF_FreshAndFurious = ::UPD.getDescription({
		Fluff = "一鼓作气！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"若本[轮|Concept.Round]中未进行过[等待|Concept.Wait]，返还使用的第一个技能" + ::MSU.Text.colorPositive("一半") + "的[行动点数|Concept.ActionPoint]。",
				"若[回合|Concept.Turn]开始时，你积累的[疲劳值|Concept.Fatigue]不低于" + ::MSU.Text.colorNegative("30%") + "，在你使用[$ $|Skill+recover_skill]前，该特技失效。"
			]
		}]
	}),
	RF_FromAllSides = ::UPD.getDescription({
		Fluff = "你学会了运用你链枷攻击的难以预知性，让敌人猜去吧！",
		Requirement = "链枷",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"链枷攻击命中会逐渐降低目标的[近战防御|Concept.MeleeDefense]和[远程防御|Concept.RangeDefense]，每叠加一层" + ::MSU.Text.colorNegative(-5) + "点，持续1[回合|Concept.Turn]。",
				"攻击命中头部时效果加倍。"
			]
		}]
	}),
	RF_FruitsOfLabor = ::UPD.getDescription({
		Fluff = "你很快就意识到，你多年的辛勤劳作，让你在佣兵工作中占尽优势！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"[生命值|Concept.Hitpoints]和[疲劳值上限|Concept.MaximumFatigue]相对各自基础值提高" + ::MSU.Text.colorPositive("10%") + "。"
			]
		}]
	}),
	RF_Ghostlike = ::UPD.getDescription({
		Fluff = "你可千万别眨眼。",
		Requirement = "护甲重量不超过20"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"接邻盟友比敌人更多时，你的下次移动无视[控制区|Concept.ZoneOfControl]。"
				"持有至多4点[触及距离|Concept.Reach]的近战武器时，如果你移动结束时接邻一名[被围攻|Concept.Surrounding]的敌人，下次攻击对其造成的伤害提高" + ::MSU.Text.colorPositive("25%") + "，穿甲伤害提高" + ::MSU.Text.colorPositive("+20%") + "。使用攻击以外的技能后失效。"
			]
		}]
	}),
	RF_HaleAndHearty = ::UPD.getDescription({
		Fluff = "多年的辛勤劳动赋予了你无与伦比的耐力！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"疲劳值恢复提高计算装备后的[疲劳值上限|Concept.MaximumFatigue]的" + ::MSU.Text.colorPositive("5%") + "。"
			]
		}]
	}),
	RF_TrickstersPurses = ::UPD.getDescription({
		Fluff = "我的包里有各种各样的好东西……",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"解锁两个额外的[背包槽位|Concept.BagSlots]。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_pocket_sand_skill]技能，使你可以在空的[背包槽位|Concept.BagSlots]中装满沙子，让周围的敌人分神。"
				]
			}
		]
	}),
	RF_HipShooter = ::UPD.getDescription({
		Fluff = "他们将在你的箭影下颤抖！",
		Requirement = "弓",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"[$ $|Skill+quick_shot]消耗的[行动点数|Concept.ActionPoints]减少" + ::MSU.Text.colorPositive(1) + "。",
				"一个[回合|Concept.Turn]当中，后续的[$ $|Skill+quick_shot]积累的[疲劳|Concept.Fatigue]增加" + ::MSU.Text.colorNegative("10%") + "。"
			]
		}]
	}),
	RF_HoldSteady = ::UPD.getDescription({
		Fluff = "指挥部队坚守阵地！",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_hold_steady_skill]技能，该技能可使你及附近盟友获得额外的[近战防御|Concept.MeleeDefense]、[远程防御|Concept.RangeDefense]和[决心|Concept.Bravery]，并免疫[$ $|Skill+stunned_effect]、击退和钩拽。"
			]
		}]
	}),
	RF_Hybridization = ::UPD.getDescription({
		Fluff = "“小斧、投斧，短矛、标枪……这不都是一样的嘛！”",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"[近战技能|Concept.MeleeSkill]和[近战防御|Concept.MeleeDefense]获得基础[远程技能|Concept.RangeSkill]" + ::MSU.Text.colorPositive("10%") + "的加值。",
				"投掷攻击的命中率提高你当前[近战技能|Concept.MeleeSkill]的" + ::MSU.Text.colorPositive("20%") + "。"
				"每[回合|Concept.Turn]免费切换成/掉投掷武器一次。不与其他免费切换物品的技能叠加。"
			]
		}]
	}),
	RF_Supporter = ::UPD.getDescription({
		Fluff = "后边交给我吧！",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"每[回合|Concept.Turn]一次，在你使用目标为接邻盟友的技能后，恢复" + ::MSU.Text.colorPositive("3") + "点[行动点数|Concept.ActionPoints]。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"获得[$ $|Skill+rf_encourage_skill]技能，使你可以提振一名盟友的[士气|Concept.Morale]。"
				]
			}
		]
	}),
	InspiringPresence = ::UPD.getDescription({
		Fluff = "站在团旗之下激励你的人超越极限。",
		Requirement = "旗帜",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"若某个友军在其[回合|Concept.Turn]开始时接邻该角色，在其[陷入近战|Concept.ZoneOfControl]或是接邻[陷入近战|Concept.ZoneOfControl]的友军时，获得" + ::MSU.Text.colorPositive("+3") + "点[行动点数|Concept.ActionPoints]。",
				"只有你的战团成员算作此[特技|Concept.Perk]的友军。"
			]
		}]
	}),
	RF_IronSights = ::UPD.getDescription({
		Fluff = "通过一点点小改造，你想法设法为远程武器安装了观瞄设备，使射击更加集中！",
		Requirement = "弩或火器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击命中头部的概率提高" + ::MSU.Text.colorPositive("25%") + "。",
				"只要对方[士气|Concept.Morale]不为" + ::Const.MoraleStateName[::Const.MoraleState.Ignore] + " ，火器爆头便会对其施加[$ $|Skill+shellshocked_effect]效果。"
			]
		}]
	}),
	RF_Kingfisher = ::UPD.getDescription({
		Fluff = "“授人以鱼不如授人以渔。”",
		Requirement = "投网",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"你的[回合|Concept.Turn]中，若你持有[网|Item+throwing_net]，攻击接邻敌人时，每次成功的近战攻击都有概率[网住|Skill+net_effect]对手，且不消耗你手中的[网。|Item+throwing_net]成功率等于攻击命中率。",
				"直到目标挣脱或死亡之前，你不能使用或换掉这张[网|Item+throwing_net]。挣脱尝试总会成功。",
				"如果你移动离开目标，目标还会被[网住|Skill+net_effect]，但你会失去这张[网|Item+throwing_net]。",
				"持有[网|Item+throwing_net]而并未[网住|Skill+net_effect]任何目标时，获得" + ::MSU.Text.colorPositive("+2") + "点[触及距离|Concept.Reach]。"
			]
		}]
	}),
	RF_KingOfAllWeapons = ::UPD.getDescription({
		Fluff = "君临天下！",
		Requirement = "矛",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击有等同于你[近战技能|Concept.MeleeSkill]" + ::MSU.Text.colorPositive("66%") + "的概率会命中敌人护甲值较低的身体部分。"
			]
		}]
	}),
	RF_Legatus = ::UPD.getDescription({
		Fluff = "征服他们！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使最多8格内的友军骷髅触发[$ $|Skill+rf_legatus_command_effect]效果。"
			]
		}]
	}),
	RF_Leverage = ::UPD.getDescription({
		Fluff = "利用武器的攻击范围，找到命中头部的角度！",
		Requirement = "最大攻击范围2格的武器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击距离为2格的目标时，命中头部概率提高" + ::MSU.Text.colorNegative("+20%") + "。"
			]
		}]
	}),
	RF_LineBreaker = ::UPD.getDescription({
		Fluff = "“给坏家伙让路！”",
		Requirement = "盾牌",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"[$ $|Skill+knock_back]的命中率提高" + ::MSU.Text.colorPositive("+15%") + "。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_shield_bash_skill]技能，该技能可使目标[茫然|Skill+dazed_effect]。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_line_breaker_skill]技能，使你可以在一次行动中击退敌人并占据其位置。"
				]
			}
		]
	}),
	RF_Poise = ::UPD.getDescription({
		Fluff = "专精中甲！可能不够灵活，但是足够轻盈！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"受到的[生命值|Concept.Hitpoints]伤害减少" + ::MSU.Text.colorPositive("30%") + "，护甲伤害减少" + ::MSU.Text.colorPositive("20%") + "。",
				"盔甲和头盔的[疲劳值上限|Concept.MaximumFatigue]减益超过35点，且超过[基础|Concept.BaseAttribute][疲劳值的|Concept.Fatigue]30%时（包括[特性|Concept.Trait]和[永久创伤|Concept.InjuryPermanent]的影响），该增益的效果开始指数下降。",
				"不影响精神攻击和状态效果的伤害，但可以帮助避免受到这些效果。",
				"攻击具有[触及劣势|Concept.ReachAdvantage]的目标时，若你的[主动值|Concept.Initiative]高于对手，劣势减" + ::MSU.Text.colorPositive(1) + "。"
				"[$ $|Perk+perk_brawny]不影响本特技。",
				"拥有[$ $|Perk+perk_nimble]或[$ $|Perk+perk_battle_forged]后不能学习。"
			]
		}]
	}),
	RF_LongReach = ::UPD.getDescription({
		Fluff = "对手盯着你的枪尖，就会忘了他的背后！",
		Requirement = "长柄武器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"盟友攻击距你两格远的敌人时，命中率计算中该敌人视为被你[围攻|Concept.Surrounding]。"
			]
		}]
	}),
	RF_ManOfSteel = ::UPD.getDescription({
		Fluff = "钢是钢铁的钢！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"受到的穿甲伤害降低等同于命中护甲当前耐久度的" + ::MSU.Text.colorPositive("10%") + "的百分比值。"
			]
		}]
	}),
	RF_Mauler = ::UPD.getDescription({
		Fluff = "血肉是你的画布！",
		Requirement = "砍刀挥砍攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"砍刀攻击额外对目标施加一层[$ $|Skill+bleeding_effect]效果。",
				"攻击已经有至少3层[$ $|Skill+bleeding_effect]的目标时，有" + ::MSU.Text.colorPositive("33%") + "概率对目标造成创伤。如果这次攻击造成了创伤，则会再造成一个。"
			]
		}]
	}),
	RF_Marksmanship = ::UPD.getDescription({
		Fluff = "靠直觉计算风向和距离，瞄准目标弱点！",
		Requirement = "远程武器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"获得你基础[远程技能|Concept.RangeSkill]的" + ::MSU.Text.colorPositive("10%") + "作为最低和最高伤害加值。"
			]
		}]
	}),
	RF_Menacing = ::UPD.getDescription({
		Fluff = "你的样子让敌人怀疑起了自己！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使接邻敌人在[士气检定|Concept.Morale]中的[决心|Concept.Bravery]降低" + ::MSU.Text.colorNegative("-10") + "点。"
			]
		}]
	}),
	RF_Mentor = ::UPD.getDescription({
		Fluff = "我将指引你成就一番伟业！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"该角色的学生获得[$ $|Skill+rf_mentors_presence_effect]效果。",
				"如果学生死亡，导师立即恢复累积[疲劳值|Concept.Fatigue]的" + ::MSU.Text.colorPositive("50%") + "，并获得[$ $|Skill+adrenaline_effect]效果。"
			]
		}]
	}),
	RF_NailedIt = ::UPD.getDescription({
		Fluff = "标枪打头，马上掉头！",
		Requirement = "远程攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击2格远的目标时，命中头部概率提高" + ::MSU.Text.colorPositive("+25%") + "。距离每拉远1格，该加成降低" + ::MSU.Text.colorNegative("-5%") + "。",
				"攻击2格远的目标时，阻挡视线惩罚降低" + ::MSU.Text.colorPositive("50%") + "。"
			]
		}]
	}),
	RF_OffhandTraining = ::UPD.getDescription({
		Fluff = "常用副手使用工具，让你拥有了令人羡慕的灵活性！",
		Requirement = "重量小于10的副手物品",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每[回合|Concept.Turn]一次，第一次使用重量小于" + ::MSU.Text.colorNegative(10) + "的副手物品不消耗[行动点数|Concept.ActionPoints]。",
				"装备网时，获得[$ $|Skill+rf_trip_artist_effect]效果。"
			]
		}]
	}),
	RF_Opportunist = ::UPD.getDescription({
		Fluff = "“队长，我没在找战利品，我在拿我的标枪呢！”",
		Requirement = "投掷武器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每场战斗中的前两次投掷攻击消耗的[行动点数|Concept.ActionPoints]" + ::MSU.Text.colorPositive("减半") + "。该效果持续到你的第二个[回合|Concept.Turn]结束为止。",
				"使用会消耗弹药的投掷武器时，在你的[回合|Concept.Turn]中，每当你在敌人尸体上结束移动时，获得" + ::MSU.Text.colorPositive(1) + "弹药。随后，下次投掷攻击" + ::MSU.Text.colorPositive("不") + "消耗[行动点数|Concept.ActionPoints]，且其积累的[疲劳值|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("50%") + "。",
				"每具尸体每场战斗中只能使用一次，不能被多个拥有此特技的角色使用。"
			]
		}]
	}),
	RF_PassingStep = ::UPD.getDescription({
		Fluff = "对步法的练习使你能绕着对手起舞！",
		Requirement = "剑",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_passing_step_skill]技能，使你可以在攻击成功后，立即无视[控制区域|Concept.ZoneOfControl]，并以更低的[行动点数|Concept.ActionPoints]和[疲劳|Concept.Fatigue]消耗移动一格。",
				"移动的目标地格必须接邻一名敌人。",
				"仅当使用双手剑或双手持握的单手剑时有效。"
			]
		}]
	}),
	RF_PatternRecognition = ::UPD.getDescription({
		Fluff = "你的经验帮助你快速适应了对手的战斗风格。",
		Requirement = "近战攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每当一名对手近战攻击你或你近战攻击一名对手时，本场战斗的剩余时间里，你对抗这名对手时，[近战技能|Concept.MeleeSkill]和[近战防御|Concept.MeleeDefense]" + ::MSU.Text.colorPositive("+3") + "，该效果叠加。",
				"总增益达到" + ::MSU.Text.colorPositive(15) + "点时，后续攻击每次只能提高" + ::MSU.Text.colorPositive("+1") + "点属性。"
			]
		}]
	}),
	RF_Phalanx = ::UPD.getDescription({
		Fluff = "学习古代结阵战斗技术。",
		Requirement = "具有穿刺攻击的双手武器，或盾牌",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"近战攻击或防御近战攻击时，每有一名持用具有穿刺攻击的双手武器或盾牌的接邻友军，" + ::MSU.Text.colorPositive("+1") + " [触及距离|Concept.Reach]。",
				"每有一名接邻友军，无视一名接邻敌人带来的[围攻|Concept.Surrounding]防御减益。拥有[$ $|Perk+perk_backstabber]特技的敌人也不例外。",
				"装备小盾时不生效。"
			]
		}]
	}),
	RF_Professional = ::UPD.getDescription({
		Fluff = "你是一名专业而老练的战士！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"随机获得你拥有的某个近战武器特技组的前两个[特技|Concept.Perk]。"
			]
		}]
	}),
	RF_PromisedPotential = ::UPD.getDescription({
		Fluff = "队长要在你身上赌一把，你可千万别让他失望。",
		Effects = [{
			Type = ::UPD.EffectType.OneTimeEffect,
			Description = [
				"升到11级时，该特技有" + ::MSU.Text.colorPositive("50%") + "概率被替换为[$ $|Perk+perk_rf_realized_potential]特技。",
				"如不成功，此特技会被替换为[$ $|Perk+perk_rf_failed_potential]特技，该特技没有任何作用。",
				"[$ $|Skill+player_character_trait]的成功概率固定为" + ::MSU.Text.colorPositive("100%") + "。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("花费过任何特技点后便无法获得。该特技不能遗忘。")
	}),
	RF_Onslaught = ::UPD.getDescription({
		Fluff = "击溃他们的队伍，击溃他们的后排，击溃他们所有人！",
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁[$ $|Skill+rf_onslaught_skill]技能，该技能会使你和临近的战团成员的[主动值|Concept.Initiative]和[近战技能|Concept.MeleeSkill]提高，还会获得一次性的[$ $|Skill+rf_line_breaker_skill]技能，持续2[轮|Concept.Round]。这次[$ $|Skill+rf_line_breaker_skill]技能消耗的[行动点数|Concept.ActionPoints]和积累的[疲劳|Concept.Fatigue]值都有所减少。"
			]
		}]
	}),
	RF_Rattle = ::UPD.getDescription({
		Fluff = "震撼敌人到骨子里去，削弱他们！",
		Requirement = "锤钝击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每次攻击都会施加[$ $|Skill+rf_rattled_effect]效果1[回合|Concept.Turn]。"
			]
		}]
	}),
	RF_RealizedPotential = ::UPD.getDescription({
		Fluff = "从衣衫褴褛到腰缠万贯！该角色走过的道路不可不谓漫长。昔日的社会底层如今已是一名羽翼丰满的雇佣兵。",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"日薪提高" + ::MSU.Text.colorNegative("100%") + "。",
				]
			},
			{
				Type = ::UPD.EffectType.OneTimeEffect,
				Description = [
					"返还所有已花费的特技点数。",
					"获得" + ::MSU.Text.colorPositive("+1") + "特技点数。",
					"随机获得" + ::MSU.Text.colorPositive("1") + "个共有（特性）特技组。",
					"随机获得" + ::MSU.Text.colorPositive("2") + "个武器特技组。",
					"所有人物属性" + ::MSU.Text.colorPositive("+15") + "。"
				]
			}
		],
		Footer = ::MSU.Text.colorNegative("该特技不能遗忘。")
	}),
	RF_Rebuke = ::UPD.getDescription({
		Fluff = "给他们点颜色看看！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"获得" + ::MSU.Text.colorPositive("25%") + "的反击概率，对相邻使用近战攻击攻击你并落空的对手施展攻击。这些攻击不消耗[行动点数|Concept.ActionPoints]，但只会在你有足够[疲劳|Concept.Fatigue]时才能触发。攻击时，你会进行一次决心检定，若检定成功，这次攻击便不积累[疲劳|Concept.Fatigue]。",
				"持有盾牌时，该概率额外提升" + ::MSU.Text.colorPositive("+15%") + "，且这些攻击不再积累[疲劳|Concept.Fatigue]。"
			]
		}]
	}),
	RF_RisingStar = ::UPD.getDescription({
		Fluff = "队长说，稳扎稳打，循序渐进，总有一天我会成为传奇！",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"下5个[等级|Concept.Level]中，[经验|Concept.Experience]获取提升" + ::MSU.Text.colorPositive("20%") + "，再之后的等级则改为提升" + ::MSU.Text.colorPositive("5%") + "。"
				]
			},
			{
				Type = ::UPD.EffectType.OneTimeEffect,
				Description = [
					"选取此特技并完成5次[升级|Concept.Level]之后，获得" + ::MSU.Text.colorPositive(2) + "点特技点数。"
				]
			}
		],
		Footer = ::MSU.Text.colorNegative("该特技不能遗忘。")
	}),
	RF_Sanguinary = ::UPD.getDescription({
		Fluff = "汩汩血泉！",
		Requirement = "砍刀挥砍攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"在你的[回合|Concept.Turn]中，你的前2次[残杀|Concept.Fatality]会分别立即为你恢复" + ::MSU.Text.colorPositive(3) + "点[行动点数|Concept.ActionPoints]。",
				"每次攻击只能触发一次。"
			]
		}]
	}),
	RF_SavageStrength = ::UPD.getDescription({
		Fluff = "兽人跟我称兄道弟！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"武器技能积累的[疲劳值|Concept.Fatigue]减少" + ::MSU.Text.colorNegative("25%") + "。"
			]
		}]
	}),
	RF_SecondWind = ::UPD.getDescription({
		Fluff = "我还没完呢！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"当你[等待|Concept.Wait]时，恢复你的[行动点数|Concept.ActionPoints]到" + ::MSU.Text.colorPositive("4") + "。"
			]
		}]
	}),
	RF_ShieldSergeant = ::UPD.getDescription({
		Fluff = "紧锁盾牌",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每场战斗开始时，装备盾的友军会免费使用[$ $|Skill+shieldwall]。",
				"两格内的友军使用[$ $|Skill+shieldwall]消耗[行动点数|Concept.ActionPoints]和积累[疲劳|Concept.Fatigue]减半。最多减至" + ::MSU.Text.colorNegative(2) + "点。",
				"如果你有[$ $|Skill+shieldwall]技能，在你身边开始或结束[回合|Concept.Turn]的友军会免费使用[$ $|Skill+shieldwall]。"
				"只要你接邻有[$ $|Skill+shieldwall]的友军开始或结束[回合|Concept.Turn]，你会免费使用[$ $|Skill+shieldwall]。"
				"对于这个[特技|Concept.Perk]来说，只有战团成员算作友军。"
			]
		}]
	}),
	RF_SmallTarget = ::UPD.getDescription({
		Fluff = "拿瓜当靶子让你爱上了打头。",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"所有攻击无论近战远程，命中头部概率提升" + ::MSU.Text.colorPositive("+10%") + "。"
			]
		}]
	}),
	RF_SoulLink = ::UPD.getDescription({
		Fluff = "直到死亡将我们分开！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"将你的灵魂和相邻友军相连，将受到的[生命值|Concept.Hitpoints]伤害的一部分转移给随机相邻友军。对其他拥有此特技的友军无效。"
			]
		}]
	}),
	RF_SteadyBrace = ::UPD.getDescription({
		Fluff = "站住不动，瞄出更精确的一击。",
		Requirement = "弩或火器",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"如果在你的[回合|Concept.Turn]中，你尚未进行过移动，弩的远程攻击的伤害穿甲率" + ::MSU.Text.colorPositive("+10%") + "，火器的命中率" + ::MSU.Text.colorPositive("+10%") + "。"
			]
		}]
	}),
	RF_StrengthInNumbers = ::UPD.getDescription({
		Fluff = "“当然了，你要面对十个拿着草叉的愤怒镇民的时候，技巧就没用了。”",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每有一个相邻友军，" + ::MSU.Text.colorPositive("+2") + "[近战技能|Concept.MeleeSkill]、[远程技能|Concept.RangeSkill]、[近战防御|Concept.MeleeDefense]和[远程防御|Concept.RangeDefense]，还会再" + ::MSU.Text.colorPositive("+5") + "[决心|Concept.Bravery]。"
			]
		}]
	}),
	RF_SurvivalInstinct = ::UPD.getDescription({
		Fluff = "你的求生欲望强烈！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每当你受到攻击时，[近战防御|Concept.MeleeDefense]和[远程防御|Concept.RangeDefense]就会提高。未命中时" + ::MSU.Text.colorPositive("+2") + "，命中时" + ::MSU.Text.colorPositive("+5") + "。未命中状态最多叠加" + ::MSU.Text.colorPositive("5") + "层，命中状态则是" + ::MSU.Text.colorPositive("2") + "层。",
				"每[回合|Concept.Turn]开始时，清空未命中带来的层数，命中的则整场战斗都会保留。"
			]
		}]
	}),
	RF_SweepingStrikes = ::UPD.getDescription({
		Fluff = "横扫武器，拒敌于外！",
		Requirement = "近战[范围|Concept.AOE]攻击"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"范围攻击无论命中与否都会使你的[触及距离|Concept.Reach]" + ::MSU.Text.colorPositive("+3") + "。此外，目标对你发起攻击时，[触及距离|Concept.Reach]" + ::MSU.Text.colorPositive("-3") + "。",
				"该[效果|Concept.StatusEffect]不叠加，持续到你下[回合|Concept.Turn]开始为止。"
			]
		}]
	}),
	RF_SwiftStabs = ::UPD.getDescription({
		Fluff = "创造破绽，结果敌人！",
		Requirement = "匕首穿刺攻击"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"主手匕首成功攻击会将其[行动点数|Concept.ActionPoints]消耗减少" + ::MSU.Text.colorPositive("2") + "，最小到" + ::MSU.Text.colorPositive("2") + "。持续到这[回合|Concept.Turn]结束。",
				"效果会在攻击落空、切换武器、更改目标、杀死目标和使用匕首攻击以外的技能时失效。"
			]
		}]
	}),
	RF_SwordmasterBladeDancer = ::UPD.getDescription({
		Fluff = "让我们舞起来！",
		Requirement = "剑"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"获得等于你装备的剑的穿甲百分比的[主动值|Concept.Initiative]。",
				"使用非刺剑时，非范围技能的[行动点数|Concept.ActionPoints]消耗减少" + ::MSU.Text.colorPositive(1) + "，积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("25%") + "。",
				"允许你在副手持有如盾牌等物品时使用[$ $|Skill+rf_passing_step_skill]。",
				"[$ $|Skill+rf_passing_step_skill]消耗的[行动点数|Concept.ActionPoints]减少" + ::MSU.Text.colorPositive(2) + "，积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive(2) + "，两者都最低减少到0。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_SwordmasterGrappler = ::UPD.getDescription({
		Fluff = "你必须自己争取这世界上的地位。",
		Requirement = "剑"
		Effects = [
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_swordmaster_kick_skill]技能，使你能趔趄目标，对其施展一次免费攻击。若攻击成功，目标会被击退一格。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_swordmaster_push_through_skill]技能，使你能趔趄目标，对其施展一次免费攻击。若攻击成功，目标会被击退一格，你会进入目标之前的位置。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_swordmaster_tackle_skill]技能，使你能对目标施展一次免费攻击。若攻击成功，目标会被[$ $|Skill+stunned_effect]，你会和目标交换位置。"
				]
			}
		],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_SwordmasterJuggernaut = ::UPD.getDescription({
		Fluff = "勇敢和愚蠢只有一线之隔。",
		Requirement = "非刺剑双手剑"
		Effects = [
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_swordmaster_charge_skill]技能，使你能用一个动作贴近并攻击目标。"
				]
			}
		],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_SwordmasterMetzger = ::UPD.getDescription({
		Fluff = "一把剑，当然也可以把某人的头砍下来！",
		Requirement = "剑"
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"使用剑时获得[$ $|Skill+decapitate]技能。",
					"获得砍刀特技组的所有特技，对于这些特技来说，剑也可以视为砍刀。",
					"剑攻击会使目标[$ $|Skill+bleeding_effect]。"
				]
			},
			{
				Type = ::UPD.EffectType.OneTimeEffect,
				Description = [
					"添加砍刀特技组到该角色的特技树中。"
				]
			}
		],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_SwordmasterPrecise = ::UPD.getDescription({
		Fluff = "让我来给你们看看，什么叫……蒙眼穿针！",
		Requirement = "剑"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每有一个角色等级，[近战技能|Concept.MeleeSkill]和[近战防御|Concept.MeleeDefense]" + ::MSU.Text.colorPositive("+1") + "，穿甲率" + ::MSU.Text.colorPositive("+1%") + "。",
				"使用刺剑时，伤害穿甲率额外提高" + ::MSU.Text.colorPositive("25%") + "。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_SwordmasterReaper = ::UPD.getDescription({
		Fluff = "收割开始了！",
		Requirement = "剑"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"剑的范围技能消耗的[行动点数|Concept.ActionPoints]减少" + ::MSU.Text.colorPositive(2) + "，积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("10%") + "。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_SwordmasterVersatileSwordsman = ::UPD.getDescription({
		Fluff = "没有稀松，样样精通。",
		Requirement = "剑"
		Effects = [{
			Type = ::UPD.EffectType.Active,
			Description = [
				"解锁三种可以在战斗中花费少量[行动点数|Concept.ActionPoints]和[疲劳|Concept.Fatigue]切换的战斗姿态，获得保持姿态就能一直生效的不同效果。",
				"[$ $|Skill+rf_swordmaster_stance_half_swording_skill]。",
				"[$ $|Skill+rf_swordmaster_stance_reverse_grip_skill]。",
				"[$ $|Skill+rf_swordmaster_stance_meisterhau_skill]。"
			]
		}],
		Footer = ::MSU.Text.colorNegative("你只能从剑术大师特技组中选取1个特技。")
	}),
	RF_TargetPractice = ::UPD.getDescription({
		Fluff = "长时间的训练使你想到了管理弹药提升精度的有效方式！",
		Requirement = "弓",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"使用远程攻击攻击持有远程武器或不在掩护中的敌人时命中率提高" + ::MSU.Text.colorPositive("+10%") + "。"
			]
		}]
	}),
	RF_Tempo = ::UPD.getDescription({
		Fluff = "掌控先机，这场战斗你说了算！",
		Requirement = "剑",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"你自己[回合|Concept.Turn]内每次命中或错过目标都会叠加" + ::MSU.Text.colorPositive(1) + "层。"
					"每层会提升你的[主动值|Concept.Initiative]" + ::MSU.Text.colorPositive("+15") + "。该加成会持续到你的下个[回合|Concept.Turn]，直到你在那个[回合|Concept.Turn]中使用了第一个技能或是[等待|Concept.Wait]为止。",
					"每个[回合|Concept.Turn]中，会获得相当于上个[回合|Concept.Turn]获得层数" + ::MSU.Text.colorPositive("一半") + "的[行动点数|Concept.ActionPoints]且每有一层，攻击积累的[疲劳|Concept.Fatigue]减少" + ::MSU.Text.colorPositive("5%") + "。"
				]
			}
		]
	}),
	RF_TerrifyingVisage = ::UPD.getDescription({
		Fluff = "直视死亡吧！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每次造成[生命值|Concept.Hitpoints]伤害都会触发精神[士气检定|Concept.Bravery]。若检定失败，目标就会陷入[惊骇|Skill+horrified_effect]。"
			]
		}]
	}),

	RF_TheRushOfBattle = ::UPD.getDescription({
		Fluff = "“记不清战斗细节也很正常，你杀的实在是太多了！”",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每当你攻击或被攻击时，获得" + ::MSU.Text.colorPositive("+5") + "[主动值|Concept.Initiative]和" + ::MSU.Text.colorPositive("+5%") + "技能[疲劳|Concept.Fatigue]减免，可以叠加，直到[回合|Concept.Turn]结束为止。分别最多叠加到" + ::MSU.Text.colorPositive("+25") + "和" + ::MSU.Text.colorPositive("+25%") + "。",
				"每[回合|Concept.Turn]获得的层数会分别记录。"
			]
		}]
	}),
	RF_ThroughTheGaps = ::UPD.getDescription({
		Fluff = "学会调度攻击，瞄准盔甲空隙！",
		Requirement = "矛的穿刺攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"攻击时，伤害穿甲率随机提高" + ::MSU.Text.colorPositive("+10%") + "到" + ::MSU.Text.colorPositive("+25%") + "。"
			]
		}]
	}),
	RF_ThroughTheRanks = ::UPD.getDescription({
		Fluff = "“我发射的东西会自己找路。”",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"远程攻击命中友军的概率降低" + ::MSU.Text.colorPositive("50%") + "。"
			]
		}]
	}),
	RF_TrickShooter = ::UPD.getDescription({
		Fluff = "趁着热，赶紧射！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"获得[$ $|Perk+perk_rf_hip_shooter]和[$ $|Perk+perk_rf_flaming_arrows]特技。"
			]
		}]
	}),
	RF_TripArtist = ::UPD.getDescription({
		Fluff = "“我会把你绊倒在地。”",
		Requirement = "装备网",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每[回合|Concept.Turn]第一次对接邻敌人成功的近战攻击会[$ $|Skill+staggered_effect]目标。",
				"使用的武器[触及|Concept.Reach]小于4时，获得与4的差值的[触及距离|Concept.Reach]，最多获得4点。"
			]
		}]
	}),
	RF_Unstoppable = ::UPD.getDescription({
		Fluff = "一旦开始行动，你就无可阻挡！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"在你的[回合|Concept.Turn]中，只要你攻击过1次，且剩余的[行动点数|Concept.ActionPoints]少于一半就会叠加1层效果，最多5层。",
				"每层会提供" + ::MSU.Text.colorPositive("+1") + "点[行动点数|Concept.ActionPoints]和" + ::MSU.Text.colorPositive("+10") + "点[主动值|Concept.Initiative]。",
				"[等待|Concept.Wait]、[$ $|Skill+recover_skill]、被[$ $|Skill+stunned_effect]、被定身、被[$ $|Skill+staggered_effect]、[回合|Concept.Turn]结束时剩余的[行动点数|Concept.ActionPoints]超过一半时，失去所有层数。"
			]
		}]
	}),
	RF_Vanquisher = ::UPD.getDescription({
		Fluff = "还有谁？",
		Effects = [
			{
				Type = ::UPD.EffectType.Passive,
				Description = [
					"每[回合|Concept.Turn]一次，杀死一名对手后，若你可以立即移入其所在的地格。下个技能的[行动点数|Concept.ActionPoints]消耗" + ::MSU.Text.colorPositive("减半") + "。"
				]
			},
			{
				Type = ::UPD.EffectType.Active,
				Description = [
					"解锁[$ $|Skill+rf_gain_ground_skill]技能，使你能在杀死一名敌人之后，立刻无视[控制区|Concept.ZoneOfControl]，消耗更少的[行动点数|Concept.ActionPoints]，移入该地格。"
				]
			}
		]
	}),
	RF_Retribution = ::UPD.getDescription({
		Fluff = "有仇必报。",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每当被击中时，你下次攻击造成的伤害提高" + ::MSU.Text.colorPositive("25%") + "。",
				"效果持续到你下次攻击或[回合|Concept.Turn]结束时为止。"
			]
		}]
	}),
	RF_VengefulSpite = ::UPD.getDescription({
		Fluff = "他们要付出代价！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每当有友军在你身边死亡时，造成的伤害提高" + ::MSU.Text.colorPositive("5%") + "，可以叠加，效果持续到本场战斗结束。"
			]
		}]
	}),
	RF_Vigilant = ::UPD.getDescription({
		Fluff = "“战场上，机会稍纵即逝！”",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"[回合|Concept.Turn]结束时，" + ::MSU.Text.colorPositive("半数") + "剩余[行动点数|Concept.ActionPoints]会留存到下个[回合，|Concept.Turn]，向下取整。"
			]
		}]
	}),
	RF_VigorousAssault = ::UPD.getDescription({
		Fluff = "你已经学会将运动时的冲力施加到武器身上！",
		Requirement = "近战或投掷攻击",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"每移动两格，你下次攻击消耗的行动点数[行动点数|Concept.ActionPoints]就减少" + ::MSU.Text.colorPositive(1) + "，最小减少到" + ::MSU.Text.colorPositive(1) + "，且积累的[疲劳|Concept.Fatigue]值减少" + ::MSU.Text.colorPositive("10%") + "。",
				"该加成会在等待、结束[回合|Concept.Turn]、使用技能时失效或切换物品时失效，切换掉/成投掷武器时除外。"
			]
		}]
	}),
	RF_WeaponMaster = ::UPD.getDescription({
		Fluff = "你已经完全明白，武器就像工具，做成各种不同的样子来应对不同的任务。于是你随身携带着一个小武器库，准备应对任何情况！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"当你装备一件武器时，若你在任意武器[特技|Concept.Perk]组中习得了第一、二个[特技|Concept.Perk]，无视[特技|Concept.Perk]层级，临时获得它武器类型对应的[特技|Concept.Perk]。",
				"若是[非混种武器|Concept.HybridWeapon]，则也会获得第三个[特技|Concept.Perk]。"
			]
		}]
	}),
	RF_WearThemDown = ::UPD.getDescription({
		Fluff = "“耍得他们团团转，躲开攻击就不难！”"
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"成功的攻击会对目标施加[$ $|Skill+rf_worn_down_effect]效果。",
				"敌人每有一项负面效果，就有" + ::MSU.Text.colorPositive("20%") + "概率需要两次成功掷骰才能命中你。这些效果包括：[$ $|Skill+rf_worn_down_effect]、[$ $|Skill+stunned_effect]、[$ $|Skill+dazed_effect]、[$ $|Skill+rf_rattled_effect]、[$ $|Skill+net_effect]、[$ $|Skill+sleeping_effect]、[$ $|Skill+staggered_effect]、[$ $|Skill+rooted_effect]和[$ $|Skill+web_effect]。"
			]
		}]
	}),
	RF_WearsItWell = ::UPD.getDescription({
		Fluff = "多年的负重劳动让你能轻松扛起佣兵装备的重量！",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"头部、身上、主手和副手装备的物品带来的[疲劳值上限|Concept.MaximumFatigue]和[主动值|Concept.Initiative]惩罚降低" + ::MSU.Text.colorPositive("20%") + "。该效果会和[$ $|Perk+perk_brawny]叠加。"
			]
		}]
	}),
	RF_WhirlingDeath = ::UPD.getDescription({
		Fluff = "旋动链枷锤头，刮起死亡旋风！",
		Requirement = "链枷",
		Effects = [{
			Type = ::UPD.EffectType.Passive,
			Description = [
				"直到你的下个[回合|Concept.Turn]开始前，每用链枷攻击1次，你的[触及距离|Concept.Reach]" + ::MSU.Text.colorPositive("+1") + "。",
				"装备双手链枷时，若攻击对象为攻击[触及距离|Concept.Reach]较低的目标，每有一点[触及距离|Concept.Reach]差距，命中头部概率提高" + ::MSU.Text.colorPositive("+10%") + "。",
				"你的[回合|Concept.Turn]中，当你使用单手链枷攻击时，对另一[触及距离|Concept.Reach]低于你的接邻敌人施展一次伤害降低" + ::MSU.Text.colorNegative("50%") + "的免费附加攻击。这次额外攻击不会提升你的[触及距离|Concept.Reach]。",
				"攻击时，无视可以无视或调整[触及距离|Concept.Reach]的能力。"
			]
		}]
	})
});

::Reforged.QueueBucket.FirstWorldInit.push(function() {
	foreach (vanillaDesc in vanillaDescriptions)
	{
		::UPD.setDescription(vanillaDesc.ID, vanillaDesc.Key, ::Reforged.Mod.Tooltips.parseString(vanillaDesc.Description));
	}

	foreach (key, string in ::Const.Strings.PerkDescription)
	{
		local parsedString = ::Reforged.Mod.Tooltips.parseString(string);
		::Const.Strings.PerkDescription[key] = parsedString;
	}

	foreach (perkDef in ::Const.Perks.LookupMap)
	{
		perkDef.Tooltip = ::Reforged.Mod.Tooltips.parseString(perkDef.Tooltip);
	}
});

::Const.Strings.Distance[4] = "遥远";
::Const.Strings.Distance[5] = "很遥远";
