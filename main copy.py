from flask import Flask, render_template, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # 用于会话管理

# 游戏数据结构
class GameEngine:
    def __init__(self):
        self.reset_game()
        
    def reset_game(self):
        # 初始化游戏状态
        self.money = 50
        self.morale = 60
        self.market_prospect = 40
        self.story_stage = 1.0
        self.meeting_count = 0
        self.game_over = False
        self.ending_type = None
        # 添加历史记录
        self.history = []
        # 记录初始状态
        self.history.append({
            'stage': 0,
            'event': '公司成立',
            'decision': '初始状态',
            'money': self.money,
            'morale': self.morale,
            'market_prospect': self.market_prospect
        })
    
    def get_current_state(self):
        return {
            'money': self.money,
            'morale': self.morale,
            'market_prospect': self.market_prospect,
            'story_stage': self.story_stage,
            'meeting_count': self.meeting_count,
            'game_over': self.game_over,
            'ending_type': self.ending_type,
            'history': self.history
        }
    
    def get_next_meeting(self):
        self.meeting_count += 1
        # 根据剧情阶段选择不同的决策问题
        if self.story_stage < 2:
            return self.get_early_stage_meeting()
        elif self.story_stage < 3:
            return self.get_mid_stage_meeting()
        elif self.story_stage < 4:
            return self.get_late_stage_meeting()
        else:
            return self.get_final_stage_meeting()
    
    def get_early_stage_meeting(self):
        meetings = [
            {
                'description': '李董事（天使投资人）敲着桌子说："公司账上资金只够撑6个月，现在有两家投资机构抛来橄榄枝，我们必须尽快定融资方案！"',
                'dilemma': '种子轮融资方案选择',
                'optionA': '接受A机构100万投资，出让15%股权，要求3个月内完成产品原型迭代。',
                'optionB': '接受B机构80万投资，出让10%股权，无明确业绩要求，但资金到账延迟1个月。',
                'impactA': {'money': 100, 'morale': 5, 'market_prospect': 10},
                'impactB': {'money': 80, 'morale': 8, 'market_prospect': 5},
                'feedbackA': '你选择接受A机构投资。充足的资金让团队能够加速产品开发，但严格的业绩要求也给团队带来了压力。',
                'feedbackB': '你选择接受B机构投资。虽然资金略少且到账延迟，但较低的股权稀释和宽松的条件让团队有更多自主权。'
            },
            {
                'description': '张技术总监（联合创始人）皱眉道："产品核心算法有两种路径，团队精力有限，只能二选一！"',
                'dilemma': '核心技术路线决策',
                'optionA': '投入40万资金，技术团队6周内自研核心算法，掌握底层知识产权但风险高。',
                'optionB': '花费25万采购第三方成熟算法授权，1个月内完成集成，快速推进原型但长期依赖供应商。',
                'impactA': {'money': -40, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': -25, 'morale': 5, 'market_prospect': 8},
                'feedbackA': '你选择自研核心算法。虽然过程艰辛，但最终成功开发出更适合产品的算法，为公司建立了技术壁垒。',
                'feedbackB': '你选择采购第三方算法。产品开发速度加快，但后续发现需要频繁支付授权费，长期成本增加。'
            },
            {
                'description': '刘市场经理急道："原型测试用户反馈功能太单一，我们是加功能还是做深核心体验？"',
                'dilemma': '产品原型迭代方向',
                'optionA': '投入15万，产品团队3周内新增3个辅助功能，满足更多用户需求但核心体验可能打折。',
                'optionB': '不新增功能，投入10万让设计团队优化核心流程，提升使用流畅度但用户新鲜感不足。',
                'impactA': {'money': -15, 'morale': 8, 'market_prospect': 8},
                'impactB': {'money': -10, 'morale': 5, 'market_prospect': 12},
                'feedbackA': '你选择增加辅助功能。用户对功能丰富度表示满意，但有反馈指出核心体验不如预期流畅。',
                'feedbackB': '你选择优化核心流程。虽然功能数量有限，但极致的用户体验获得了测试用户的高度评价。'
            },
            {
                'description': '王财务负责人递上报表："本月资金消耗超预期，研发和市场只能保一个方向的预算！"',
                'dilemma': '初期资金分配优先级',
                'optionA': '冻结市场推广预算，将剩余20万全部投入研发，确保原型按时完成但无用户曝光。',
                'optionB': '削减研发预算10万，将15万用于行业展会和社群推广，积累潜在用户但原型迭代延迟2周。',
                'impactA': {'money': -20, 'morale': -5, 'market_prospect': 5},
                'impactB': {'money': -15, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择全力投入研发。产品质量得到保证，但市场认知度不足，后续推广难度增加。',
                'feedbackB': '你选择平衡研发和市场。虽然产品延迟，但提前积累了一批种子用户，为正式发布打下基础。'
            },
            {
                'description': '陈HR主管低声说："核心前端工程师收到竞品offer，薪资比我们高30%，留不留？"',
                'dilemma': '核心初创人才挽留',
                'optionA': '一次性支付10万签字费，月薪上调20%，要求签订2年竞业协议，留住人才但现金流压力大。',
                'optionB': '拒绝加薪，承诺产品上线后给予2%期权，节省当前资金但人才流失风险极高。',
                'impactA': {'money': -25, 'morale': 15, 'market_prospect': 8},
                'impactB': {'money': 0, 'morale': -10, 'market_prospect': -10},
                'feedbackA': '你选择高薪挽留核心人才。团队稳定性得到保障，开发进度顺利，但短期内资金压力增大。',
                'feedbackB': '你选择用期权替代加薪。核心工程师最终离职，项目进度严重延误，团队士气受挫。'
            },
            {
                'description': '李产品经理拿着用户问卷："封闭测试用户反馈两极分化，我们是快速迭代还是先验证需求？"',
                'dilemma': '早期用户反馈处理策略',
                'optionA': '投入8万，组织5场线下用户访谈，2周内明确需求痛点后再迭代，精准但耗时。',
                'optionB': '不做额外调研，投入12万让研发团队4周内快速迭代3个版本，覆盖不同用户诉求但可能做无用功。',
                'impactA': {'money': -8, 'morale': 5, 'market_prospect': 12},
                'impactB': {'money': -12, 'morale': 8, 'market_prospect': 6},
                'feedbackA': '你选择深入调研需求。基于用户访谈结果的迭代版本获得了极高评价，用户满意度大幅提升。',
                'feedbackB': '你选择快速迭代。虽然覆盖了多种用户需求，但资源分散导致每个版本的改进都不够深入。'
            },
            {
                'description': '张法务顾问提醒："产品涉及用户数据收集，合规资质还在申请中，要不要等资质？"',
                'dilemma': '合规与快速上线的平衡',
                'optionA': '暂停上线计划，投入15万委托律所加急办理合规资质，1个月内完成，无法律风险但错失市场窗口期。',
                'optionB': '放弃加急办理，节省15万，产品立即上线公测，标注"beta版"规避部分风险但可能被监管处罚。',
                'impactA': {'money': -15, 'morale': 3, 'market_prospect': 10},
                'impactB': {'money': 0, 'morale': 8, 'market_prospect': -5},
                'feedbackA': '你选择等待合规资质。虽然延迟上线，但合规先行的策略为公司赢得了良好声誉，也避免了潜在风险。',
                'feedbackB': '你选择立即上线。用户增长迅速，但随后收到监管警告，不得不暂停部分功能进行整改。'
            },
            {
                'description': '刘合作方代表来电："有一家行业大厂愿意提供资源支持，但要求我们接入他们的生态，要不要同意？"',
                'dilemma': '早期合作模式选择',
                'optionA': '接入大厂生态，获得免费服务器资源和10万曝光量，但需开放核心数据接口，丧失部分独立性。',
                'optionB': '拒绝接入，自建服务器（投入18万），独立运营但曝光不足，获客成本翻倍。',
                'impactA': {'money': 0, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': -18, 'morale': 5, 'market_prospect': 5},
                'feedbackA': '你选择接入大厂生态。用户量快速增长，但随着对大厂依赖加深，产品迭代方向开始受到限制。',
                'feedbackB': '你选择独立运营。保持了产品的独立性和数据控制权，但初期获客成本高，增长速度较慢。'
            },
            {
                'description': '王行政主管汇报："当前共享工位租期快到，是续租还是租独立办公室？"',
                'dilemma': '办公成本与团队氛围平衡',
                'optionA': '花费24万租下100㎡独立办公室，租期1年，提升团队归属感但增加固定成本。',
                'optionB': '续租共享工位，年花费12万，节省资金但办公环境嘈杂，影响研发效率。',
                'impactA': {'money': -24, 'morale': 15, 'market_prospect': 8},
                'impactB': {'money': -12, 'morale': -5, 'market_prospect': -5},
                'feedbackA': '你选择租独立办公室。团队工作环境改善，协作效率提升，员工归属感增强。',
                'feedbackB': '你选择续租共享工位。虽然节省了资金，但嘈杂的环境导致工作效率下降，部分员工开始抱怨。'
            },
            {
                'description': '李市场经理提议："原型完成后，我们是做封闭内测还是公开公测？"',
                'dilemma': '产品测试范围决策',
                'optionA': '投入5万筛选500名精准用户封闭内测，收集高质量反馈但曝光有限。',
                'optionB': '投入8万在科技媒体做公开公测，吸引1万+用户参与，快速积累数据但需应对大量负面反馈。',
                'impactA': {'money': -5, 'morale': 8, 'market_prospect': 8},
                'impactB': {'money': -8, 'morale': -3, 'market_prospect': 15},
                'feedbackA': '你选择封闭内测。收到的反馈质量高且有针对性，团队能够专注解决核心问题。',
                'feedbackB': '你选择公开公测。用户量激增，但大量负面反馈让团队压力倍增，需要快速应对各种问题。'
            },
            {
                'description': '张技术总监无奈道："硬件原型的核心组件供应商，选小厂还是大厂？"',
                'dilemma': '供应链成本与稳定性选择',
                'optionA': '选择小厂供应商，组件单价低30%，投入12万采购，但交货周期不确定（可能延迟1个月）。',
                'optionB': '选择大厂供应商，投入18万采购，价格高但48小时内交货，确保原型测试按时推进。',
                'impactA': {'money': -12, 'morale': -5, 'market_prospect': -5},
                'impactB': {'money': -18, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择小厂供应商。果然遭遇交货延迟，导致原型测试推迟，错过重要展会。',
                'feedbackB': '你选择大厂供应商。虽然成本较高，但供应链稳定，产品开发进度得以保证。'
            },
            {
                'description': '刘创始人叹气："最近既要盯研发进度，又要对接投资人，精力根本不够用！"',
                'dilemma': '创始人精力分配',
                'optionA': '花费15万聘请专职融资顾问，负责对接投资人，创始人专注研发但增加成本。',
                'optionB': '不聘请顾问，创始人牺牲研发管理时间，每周花4天对接融资，节省资金但研发进度可能滞后。',
                'impactA': {'money': -15, 'morale': 10, 'market_prospect': 12},
                'impactB': {'money': 0, 'morale': -8, 'market_prospect': 5},
                'feedbackA': '你选择聘请融资顾问。创始人能够专注产品研发，团队效率提升，同时融资进展顺利。',
                'feedbackB': '你选择亲自对接融资。虽然节省了顾问费用，但研发进度受到影响，团队沟通不畅。'
            }
        ]
        return random.choice(meetings)
    
    def get_mid_stage_meeting(self):
        meetings = [
            {
                'description': '市场总监兴奋地说："CEO，我们的产品在某个新兴市场取得了突破性进展，用户增长率超过预期！但要扩大市场份额，需要大量营销投入。"',
                'dilemma': '是否加大新兴市场的营销投入？',
                'optionA': '全面发力。投入大量资金进行市场推广，争取快速占领市场。',
                'optionB': '稳步推进。保持适度投入，确保资金安全的同时缓慢扩大影响力。',
                'impactA': {'money': -18, 'morale': 8, 'market_prospect': 12},
                'impactB': {'money': -5, 'morale': 5, 'market_prospect': 6},
                'feedbackA': '你决定全面发力新兴市场。大规模的营销活动确实带来了用户爆炸式增长，但也消耗了大量资金，公司财务状况变得紧张。',
                'feedbackB': '你选择稳步推进策略。虽然增长速度不如激进策略，但公司保持了良好的现金流，团队压力也相对较小。'
            },
            {
                'description': '人力资源总监担忧地说："CEO，随着公司快速发展，核心团队成员开始接到竞争对手的挖角邀请，我们需要调整薪资结构。"',
                'dilemma': '如何应对人才流失风险？',
                'optionA': '大幅加薪。提高核心员工薪资，留住人才，但增加成本负担。',
                'optionB': '股权激励。提供期权激励，但短期激励效果有限。',
                'impactA': {'money': -15, 'morale': 12, 'market_prospect': 5},
                'impactB': {'money': -3, 'morale': 8, 'market_prospect': 3},
                'feedbackA': '你决定大幅提高核心员工薪资。这一举措成功留住了关键人才，团队士气高涨，但公司利润率受到明显影响。',
                'feedbackB': '你选择实施股权激励计划。虽然短期内有几位核心员工离职，但大多数员工对长期发展前景充满信心，选择留下。'
            },
            {
                'description': '财务总监谨慎地说："CEO，我们收到了一家大型科技公司的收购意向。他们开出了不错的价格，但接受收购意味着失去独立性。"',
                'dilemma': '是否接受收购要约？',
                'optionA': '接受收购。获得丰厚回报，但失去对公司的控制权。',
                'optionB': '拒绝收购。保持独立性，继续发展，但可能错过好机会。',
                'impactA': {'money': 30, 'morale': -8, 'market_prospect': -10},
                'impactB': {'money': 5, 'morale': 15, 'market_prospect': 10},
                'feedbackA': '你接受了收购要约。投资者获得了丰厚回报，但部分员工对公司未来发展方向产生疑虑，开始寻找新机会。',
                'feedbackB': '你拒绝了收购，选择独立发展。团队对这一决定表示赞赏，认为公司有更大的发展潜力，但也面临着更激烈的市场竞争。'
            },
            {
                'description': '法务总监紧急汇报："CEO，我们发现有竞争对手在市场上散布关于我们产品安全漏洞的不实信息，这已经影响到我们的客户签约。"',
                'dilemma': '如何应对竞争对手的负面谣言？',
                'optionA': '法律诉讼。起诉竞争对手散布谣言，但这会消耗大量资源并可能延长品牌受损时间。',
                'optionB': '公开澄清。通过媒体和用户社区积极澄清事实，但可能进一步放大负面影响。',
                'impactA': {'money': -12, 'morale': 5, 'market_prospect': -3},
                'impactB': {'money': -5, 'morale': 8, 'market_prospect': 5},
                'feedbackA': '你选择了法律诉讼。经过漫长的法律程序，最终胜诉并获得赔偿，但在此期间市场份额已有所损失。',
                'feedbackB': '你选择公开澄清事实。透明的做法赢得了客户的信任，大多数客户选择继续合作，品牌声誉反而得到了提升。'
            },
            {
                'description': '产品总监提议："CEO，我们的数据显示，用户对我们的产品有强烈的付费意愿，但当前的免费功能过多，影响了转化率。"',
                'dilemma': '是否调整产品的免费功能范围？',
                'optionA': '缩小免费功能。将部分高级功能转为付费，提高转化率，但可能失去部分免费用户。',
                'optionB': '保持现状。继续提供丰富的免费功能，扩大用户基础，但收入增长缓慢。',
                'impactA': {'money': 15, 'morale': -5, 'market_prospect': 8},
                'impactB': {'money': 3, 'morale': 5, 'market_prospect': 12},
                'feedbackA': '你决定缩小免费功能范围。付费转化率显著提高，公司收入迅速增长，但部分免费用户流失，社交媒体上出现了一些负面评价。',
                'feedbackB': '你选择保持现有模式。用户数量继续快速增长，品牌知名度提升，但收入增长不及预期，财务压力增大。'
            },
            {
                'description': '销售总监汇报："CEO，我们发现有几位高价值客户对我们的产品提出了相同的功能建议，实现这些功能需要大量研发投入。"',
                'dilemma': '是否为重要客户定制专属功能？',
                'optionA': '优先开发。投入资源开发客户需求的功能，巩固大客户关系，但可能影响产品路线图。',
                'optionB': '统一规划。坚持产品整体规划，拒绝特殊定制，但可能失去重要客户。',
                'impactA': {'money': -10, 'morale': 5, 'market_prospect': 15},
                'impactB': {'money': -8, 'morale': 8, 'market_prospect': -5},
                'feedbackA': '你决定优先开发客户需求的功能。这一决定赢得了大客户的信任，他们不仅续签了合同，还带来了新的客户推荐。',
                'feedbackB': '你选择坚持统一的产品规划。虽然短期内失去了几位客户，但产品愿景更加清晰，长期发展路径更加明确。'
            }
        ]
        return random.choice(meetings)
    
    def get_late_stage_meeting(self):
        meetings = [
            {
                'description': 'CEO，我们的产品已经具备了上市条件，但市场环境变化迅速，竞争对手也在积极筹备IPO。我们需要决定上市时机。',
                'dilemma': '何时启动IPO进程？',
                'optionA': '立即启动。抓住当前市场机会，但准备工作可能不够充分。',
                'optionB': '延迟上市。完善公司治理和财务结构，但可能错过最佳窗口。',
                'impactA': {'money': 25, 'morale': 10, 'market_prospect': -5},
                'impactB': {'money': -8, 'morale': 5, 'market_prospect': 15},
                'feedbackA': '你决定立即启动IPO。市场反应热烈，公司估值超出预期，但上市后的严格监管也给团队带来了新的压力。',
                'feedbackB': '你选择延迟IPO，继续完善公司。虽然短期没有获得资金，但公司治理结构更加健全，为未来的长期发展奠定了坚实基础。'
            },
            {
                'description': 'CEO，我们面临着一个重要的战略选择：是继续专注于现有业务，还是多元化发展进入新领域？',
                'dilemma': '是否进行业务多元化？',
                'optionA': '专注主业。深耕现有市场，巩固领先地位。',
                'optionB': '多元发展。进入新领域，分散风险，寻找增长点。',
                'impactA': {'money': 10, 'morale': 8, 'market_prospect': 10},
                'impactB': {'money': -20, 'morale': 12, 'market_prospect': 5},
                'feedbackA': '你选择专注于主营业务。这一策略让公司在核心领域建立了更强大的竞争壁垒，市场份额稳步提升。',
                'feedbackB': '你决定多元化发展。虽然初期投入巨大，但新业务线展现出良好的增长潜力，为公司打开了新的发展空间。'
            },
            {
                'description': 'CEO，我们发现一个重要的技术创新机会，但研发投入巨大，且成功概率不确定。这可能是改变行业格局的机会。',
                'dilemma': '是否投入大量资源进行高风险技术创新？',
                'optionA': '冒险投入。押注未来技术趋势，可能带来巨大回报。',
                'optionB': '保守发展。专注于现有技术的优化和应用。',
                'impactA': {'money': -25, 'morale': 15, 'market_prospect': 20},
                'impactB': {'money': 15, 'morale': 5, 'market_prospect': 8},
                'feedbackA': '你决定冒险投入新技术研发。这一决定激发了团队的创新热情，虽然消耗了大量资金，但初步成果令人振奋。',
                'feedbackB': '你选择保守发展策略。公司保持了稳定的盈利能力，现有产品不断优化，但在行业技术变革中可能面临被赶超的风险。'
            },
            {
                'description': 'CEO，我们收到了国际市场拓展的绝佳机会，但需要大量资金支持海外团队建设和本地化开发。',
                'dilemma': '是否进行国际化扩张？',
                'optionA': '积极出海。投入资金开拓国际市场，寻求更大增长空间。',
                'optionB': '立足国内。巩固国内市场地位，暂缓国际化步伐。',
                'impactA': {'money': -22, 'morale': 10, 'market_prospect': 18},
                'impactB': {'money': 10, 'morale': 5, 'market_prospect': 5},
                'feedbackA': '你决定积极开拓国际市场。虽然前期投入巨大，但海外业务逐渐实现盈利，公司国际化战略取得初步成功。',
                'feedbackB': '你选择立足国内市场。公司在国内市场的主导地位进一步巩固，但国际市场的竞争格局正在快速形成。'
            },
            {
                'description': 'CEO，我们的某个产品线出现了重大安全漏洞，需要立即采取行动。修复漏洞需要召回产品并进行补偿。',
                'dilemma': '如何处理产品安全危机？',
                'optionA': '主动召回。立即召回问题产品并全额退款，但将面临巨大财务损失。',
                'optionB': '低调处理。只针对出现问题的用户进行修复和补偿，降低损失。',
                'impactA': {'money': -20, 'morale': 8, 'market_prospect': 3},
                'impactB': {'money': -5, 'morale': -5, 'market_prospect': -15},
                'feedbackA': '你决定主动召回所有问题产品。这一负责任的做法赢得了用户和行业的尊重，虽然短期损失巨大，但品牌信任度得到了提升。',
                'feedbackB': '你选择低调处理危机。虽然减少了直接经济损失，但随着更多用户发现问题，负面评价开始蔓延，品牌形象受到严重损害。'
            },
            {
                'description': 'CEO，我们的主要供应商提出了新的合作条件，要求提高产品价格，但同时愿意提供更优惠的独家合作协议。',
                'dilemma': '是否接受供应商的新条件？',
                'optionA': '接受独家协议。锁定稳定供应链，但成本上升且依赖单一供应商。',
                'optionB': '寻找新供应商。保持议价能力，但可能面临供应链不稳定风险。',
                'impactA': {'money': -12, 'morale': 5, 'market_prospect': 8},
                'impactB': {'money': 3, 'morale': -3, 'market_prospect': -5},
                'feedbackA': '你接受了独家合作协议。虽然成本上升，但供应链稳定性大幅提高，产品交付更加可靠，客户满意度提升。',
                'feedbackB': '你决定寻找新的供应商。通过引入竞争，你获得了更优惠的价格，但新供应商的产品质量和交付稳定性尚需验证。'
            }
        ]
        return random.choice(meetings)
    
    def get_final_stage_meeting(self):
        meetings = [
            {
                'description': 'CEO，经过多年发展，我们已经成为行业的重要玩家。现在面临最终的战略选择：是继续扩张成为行业巨头，还是寻求最佳的退出机会？',
                'dilemma': '公司的最终发展战略是什么？',
                'optionA': '全面扩张。投入所有资源争取行业领导地位。',
                'optionB': '战略退出。寻找合适的并购方，实现公司价值。',
                'impactA': {'money': -30, 'morale': 20, 'market_prospect': 25},
                'impactB': {'money': 40, 'morale': -10, 'market_prospect': -5},
                'feedbackA': '你选择全面扩张战略。公司进入快速增长轨道，市场份额大幅提升，成为行业领导者，但也背负了沉重的财务负担。',
                'feedbackB': '你选择战略退出。公司被一家国际巨头收购，股东获得丰厚回报，但许多员工对公司文化的变化感到担忧。'
            },
            {
                'description': 'CEO，我们收到了多家投资机构的融资意向，估值都非常可观。同时，我们也有能力通过自身盈利实现独立发展。',
                'dilemma': '是否接受新一轮融资？',
                'optionA': '接受融资。获得充足资金加速发展，但稀释现有股权。',
                'optionB': '保持独立。依靠自身盈利发展，但可能错失快速扩张机会。',
                'impactA': {'money': 35, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': 10, 'morale': 15, 'market_prospect': 10},
                'feedbackA': '你接受了新一轮融资。充足的资金让公司能够进行更大规模的市场扩张和技术投入，市场地位进一步巩固。',
                'feedbackB': '你选择保持独立发展。公司通过自身盈利实现稳健增长，保持了对业务的完全控制权，但增长速度相对保守。'
            },
            {
                'description': 'CEO，我们的研究部门发现了一项可能彻底改变行业格局的颠覆性技术，但需要投入天文数字的研发资金，且成功几率极低。',
                'dilemma': '是否投入巨资研发颠覆性技术？',
                'optionA': '全力研发。投入大部分资金进行攻关，可能带来革命性突破。',
                'optionB': '谨慎投入。小比例投资探索可能性，主要资金用于现有业务巩固。',
                'impactA': {'money': -40, 'morale': 25, 'market_prospect': 30},
                'impactB': {'money': -5, 'morale': 10, 'market_prospect': 8},
                'feedbackA': '你决定全力研发颠覆性技术。虽然投入巨大，但突破性进展让公司在行业中占据了绝对领先地位，开创了新的市场空间。',
                'feedbackB': '你选择谨慎投入策略。在保持业务稳定的同时，也为未来技术发展保留了可能性，公司继续保持着稳健增长。'
            },
            {
                'description': 'CEO，随着公司规模不断扩大，我们面临着组织架构调整的挑战。当前结构已经开始影响决策效率和创新速度。',
                'dilemma': '如何进行组织架构调整？',
                'optionA': '扁平化改革。大幅减少管理层级，提高决策效率，但可能增加失控风险。',
                'optionB': '矩阵式管理。建立跨部门协作机制，增强专业性，但可能导致决策流程复杂。',
                'impactA': {'money': -8, 'morale': 15, 'market_prospect': 12},
                'impactB': {'money': -12, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你推动了扁平化改革。组织变得更加敏捷，创新速度明显提升，但随着规模扩大，管理半径增大带来的挑战也日益显现。',
                'feedbackB': '你选择了矩阵式管理结构。专业分工更加明确，跨部门协作有所改善，但初期的适应成本较高，决策效率暂时下降。'
            },
            {
                'description': 'CEO，我们面临着前所未有的行业监管变化，新政策将大幅提高合规成本，但也会淘汰一批不合规的竞争对手。',
                'dilemma': '如何应对行业监管变化？',
                'optionA': '主动合规。投入资源提前满足新规要求，建立合规优势。',
                'optionB': '观望调整。待政策明确后再做应对，避免过度投入。',
                'impactA': {'money': -18, 'morale': 5, 'market_prospect': 20},
                'impactB': {'money': 5, 'morale': -5, 'market_prospect': -8},
                'feedbackA': '你选择主动合规。公司不仅顺利通过了监管检查，还因为高标准的合规体系赢得了客户和监管机构的信任，市场份额显著提升。',
                'feedbackB': '你采取观望态度。当政策正式实施时，公司不得不仓促应对，短期内合规成本激增，业务拓展受到严重影响。'
            }
        ]
        return random.choice(meetings)
    
    def make_decision(self, option):
        # 应用决策影响
        if option == 'A':
            impact = self.current_meeting['impactA']
            feedback = self.current_meeting['feedbackA']
            decision_text = f"选择A: {self.current_meeting['optionA'][:50]}..."
        else:
            impact = self.current_meeting['impactB']
            feedback = self.current_meeting['feedbackB']
            decision_text = f"选择B: {self.current_meeting['optionB'][:50]}..."
        
        # 记录决策前的状态
        prev_money = self.money
        prev_morale = self.morale
        prev_market = self.market_prospect
        
        # 更新游戏状态
        self.money = max(0, min(100, self.money + impact['money']))
        self.morale = max(0, min(100, self.morale + impact['morale']))
        self.market_prospect = max(0, min(100, self.market_prospect + impact['market_prospect']))
        self.story_stage += 0.2
        
        # 添加历史记录
        self.history.append({
            'stage': self.story_stage - 0.2,  # 记录决策时的阶段
            'event': self.current_meeting['dilemma'],
            'decision': decision_text,
            'feedback': feedback,
            'money': self.money,
            'morale': self.morale,
            'market_prospect': self.market_prospect,
            'money_change': impact['money'],
            'morale_change': impact['morale'],
            'market_prospect_change': impact['market_prospect']
        })
        
        # 检查失败条件
        if self.money <= 0:
            self.game_over = True
            self.ending_type = 'bankruptcy'
        elif self.morale <= 0:
            self.game_over = True
            self.ending_type = 'team_disband'
        elif self.market_prospect <= 0:
            self.game_over = True
            self.ending_type = 'product_failure'
        # 检查是否达到最终阶段
        elif self.story_stage >= 5:
            self.game_over = True
            self.determine_final_ending()
        
        return {
            'feedback': feedback,
            'money_change': impact['money'],
            'morale_change': impact['morale'],
            'market_prospect_change': impact['market_prospect'],
            'current_state': self.get_current_state()
        }
    
    def determine_final_ending(self):
        # 根据最终状态决定结局
        avg_score = (self.money + self.morale + self.market_prospect) / 3
        if avg_score >= 80:
            self.ending_type = 'successful_ipo'
        elif avg_score >= 60:
            self.ending_type = 'acquisition'
        elif avg_score >= 40:
            self.ending_type = 'survival'
        else:
            self.ending_type = 'struggle'
    
    def get_ending_text(self):
        endings = {
            'bankruptcy': '【游戏结束】公司资金耗尽，宣布破产。作为CEO，你未能带领公司度过难关，投资者对你的领导能力失去信心。',
            'team_disband': '【游戏结束】团队士气崩溃，核心成员纷纷离职。没有了优秀的团队，公司无法继续运营，最终被市场淘汰。',
            'product_failure': '【游戏结束】市场前景黯淡，产品失去竞争力。公司无法吸引新用户，现有用户也逐渐流失，最终不得不关闭业务。',
            'successful_ipo': '【胜利】恭喜！在你的领导下，公司成功上市，市值超过预期。你被誉为创业传奇，成为行业标杆。',
            'acquisition': '【成功】公司被行业巨头高价收购。虽然失去了独立性，但股东获得了丰厚回报，你也被任命为重要职位。',
            'survival': '【结局】公司成功生存下来，并在市场中占据了一席之地。虽然没有取得巨大成功，但为未来的发展奠定了基础。',
            'struggle': '【结局】公司勉强维持运营。在激烈的市场竞争中，你需要继续努力才能让公司走向更好的未来。'
        }
        return endings.get(self.ending_type, '')

# 全局游戏引擎实例
game_engine = GameEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/start_game', methods=['POST'])
def start_game():
    game_engine.reset_game()
    game_engine.current_meeting = game_engine.get_next_meeting()
    return jsonify({
        'meeting_count': game_engine.meeting_count,
        'description': game_engine.current_meeting['description'],
        'dilemma': game_engine.current_meeting['dilemma'],
        'optionA': game_engine.current_meeting['optionA'],
        'optionB': game_engine.current_meeting['optionB'],
        'current_state': game_engine.get_current_state()
    })

@app.route('/api/make_decision', methods=['POST'])
def make_decision():
    data = request.json
    option = data.get('option')
    
    result = game_engine.make_decision(option)
    
    response = {
        'feedback': result['feedback'],
        'money_change': result['money_change'],
        'morale_change': result['morale_change'],
        'market_prospect_change': result['market_prospect_change'],
        'current_state': result['current_state']
    }
    
    # 如果游戏未结束，获取下一次会议
    if not game_engine.game_over:
        game_engine.current_meeting = game_engine.get_next_meeting()
        response['next_meeting'] = {
            'meeting_count': game_engine.meeting_count,
            'description': game_engine.current_meeting['description'],
            'dilemma': game_engine.current_meeting['dilemma'],
            'optionA': game_engine.current_meeting['optionA'],
            'optionB': game_engine.current_meeting['optionB']
        }
    else:
        response['ending_text'] = game_engine.get_ending_text()
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)