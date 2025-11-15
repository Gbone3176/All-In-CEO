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
        elif self.story_stage < 5:
            return self.get_final_stage_meeting()
        else:
            return self.get_post_ipo_stage_meeting()
    
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
                'description': '李市场总监展示数据："产品上线1个月，用户增长缓慢，要不要烧钱换量？"',
                'dilemma': '用户增长策略选择',
                'optionA': '投入50万用于抖音/小红书信息流投放，定向25-35岁职场人群，为期2个月，快速拉新但ROI不确定。',
                'optionB': '不做付费投放，投入15万搭建用户推荐体系，奖励老用户拉新（每成功邀请1人送30元优惠券），低成本但增长缓慢。',
                'impactA': {'money': -50, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': -15, 'morale': 5, 'market_prospect': 8},
                'feedbackA': '你选择大规模投放广告。短期内用户量激增，但获客成本高于预期，转化率偏低，资金消耗过快。',
                'feedbackB': '你选择搭建推荐体系。虽然增长速度较慢，但用户质量高，留存率显著提升，长期效果更好。'
            },
            {
                'description': '张产品总监汇报："用户反馈功能不够用，但核心体验还有优化空间，资源该倾向哪？"',
                'dilemma': '功能迭代与体验优化平衡',
                'optionA': '投入30万，研发团队6周内新增5个高频需求功能，提升用户留存但可能引入新bug。',
                'optionB': '投入20万，测试团队和设计团队4周内修复10个现有bug，优化3个核心流程，提升口碑但功能新鲜感不足。',
                'impactA': {'money': -30, 'morale': 10, 'market_prospect': 8},
                'impactB': {'money': -20, 'morale': 5, 'market_prospect': 12},
                'feedbackA': '你选择新增功能。用户对新功能反响积极，但随之而来的稳定性问题也引发了一些抱怨。',
                'feedbackB': '你选择优化体验。产品稳定性和流畅度大幅提升，App Store评分从3.5星上升到4.8星，但用户期待更多新功能。'
            },
            {
                'description': '王财务总监提醒："天使轮资金快用一半了，要不要开始尝试盈利？"',
                'dilemma': '盈利模式启动时机',
                'optionA': '上线广告变现功能，在产品首页嵌入3个轻度广告位，预计月入8万，但可能影响用户体验。',
                'optionB': '暂不广告变现，投入25万研发付费会员体系（月费20元，含专属功能），2个月后上线，长期收益但短期无收入。',
                'impactA': {'money': 8, 'morale': -5, 'market_prospect': -5},
                'impactB': {'money': -25, 'morale': 8, 'market_prospect': 15},
                'feedbackA': '你选择广告变现。立即获得收入，但部分用户因广告体验流失，付费意愿明显降低。',
                'feedbackB': '你选择开发会员体系。初期投入大，但上线后会员转化率达15%，长期收益可观，用户满意度高。'
            },
            {
                'description': '刘HR经理着急道："3名核心研发工程师同时提出离职，原因是加班多且薪资无竞争力！"',
                'dilemma': '核心员工留存策略',
                'optionA': '投入40万为核心员工普涨薪资25%，优化加班制度（每月最多加班4天），留住人才但增加人力成本。',
                'optionB': '不涨薪，投入15万招聘2名资深猎头，1个月内招聘替代人员，节省资金但项目交接可能出现断层。',
                'impactA': {'money': -40, 'morale': 15, 'market_prospect': 10},
                'impactB': {'money': -15, 'morale': -10, 'market_prospect': -8},
                'feedbackA': '你选择提高薪资待遇。核心团队稳定性得到保障，产品开发进度顺利，创新氛围浓厚。',
                'feedbackB': '你选择招聘新人。老员工离职导致项目延迟，新人上手需要时间，团队协作效率下降。'
            },
            {
                'description': '李渠道经理提议："现在有两种市场渠道，我们该重点布局哪一个？"',
                'dilemma': '市场渠道选择',
                'optionA': '投入35万与3家行业垂直媒体合作，发布深度评测和案例，精准触达目标用户但覆盖范围窄。',
                'optionB': '投入40万在3个一线城市做线下地推（写字楼/创业园区），发放试用礼品，覆盖广但获客成本高。',
                'impactA': {'money': -35, 'morale': 8, 'market_prospect': 12},
                'impactB': {'money': -40, 'morale': 10, 'market_prospect': 8},
                'feedbackA': '你选择垂直媒体合作。专业内容获得目标用户高度认可，转化率达8%，远超行业平均水平。',
                'feedbackB': '你选择线下地推。品牌曝光度提升，但转化率仅为2%，投资回报率偏低。'
            },
            {
                'description': '张技术总监紧急汇报："昨晚收到大量用户投诉，核心功能出现崩溃bug，同时新功能迭代在即！"',
                'dilemma': '紧急bug修复与新功能迭代冲突',
                'optionA': '暂停新功能开发，全员投入bug修复，48小时内解决问题，保障用户体验但新功能延迟1个月上线。',
                'optionB': '留30%研发人员修复bug（预计7天解决），其余人员继续推进新功能，确保迭代节奏但用户投诉可能持续。',
                'impactA': {'money': -5, 'morale': -5, 'market_prospect': 15},
                'impactB': {'money': -3, 'morale': 8, 'market_prospect': -10},
                'feedbackA': '你选择优先修复bug。快速解决了用户痛点，用户满意度迅速回升，品牌声誉得到维护。',
                'feedbackB': '你选择并行处理。新功能如期发布，但bug修复延迟，大量用户流失到竞品。'
            },
            {
                'description': '刘产品经理分析数据："高端用户愿意付费，下沉市场用户量大但付费意愿低，该侧重哪类？"',
                'dilemma': '用户分层运营策略',
                'optionA': '投入25万研发高端付费模块（年费399元，含专属客服+定制功能），聚焦高净值用户但放弃部分下沉市场。',
                'optionB': '投入18万优化产品轻量化版本，降低使用门槛，吸引下沉市场用户，提升用户基数但短期盈利困难。',
                'impactA': {'money': 40, 'morale': 8, 'market_prospect': 8},
                'impactB': {'money': -18, 'morale': 10, 'market_prospect': 15},
                'feedbackA': '你选择高端用户策略。付费收入显著提升，客单价达280元，但用户增长速度放缓。',
                'feedbackB': '你选择下沉市场策略。用户量突破100万，但付费转化率不足2%，现金流压力增大。'
            },
            {
                'description': '王技术架构师担忧："用户量突破10万后，现有服务器频繁卡顿，该怎么解决？"',
                'dilemma': '服务器扩容方案选择',
                'optionA': '投入30万升级云服务器配置（CPU/内存翻倍），1周内完成部署，保障稳定性但成本高。',
                'optionB': '投入15万研发服务器负载均衡算法，2周内完成优化，节省成本但可能仍有偶尔卡顿。',
                'impactA': {'money': -30, 'morale': 12, 'market_prospect': 10},
                'impactB': {'money': -15, 'morale': 5, 'market_prospect': 5},
                'feedbackA': '你选择升级服务器。系统性能立即提升，用户体验明显改善，投诉量下降80%。',
                'feedbackB': '你选择自研负载均衡。成本节约了一半，但高峰期仍有轻微卡顿，用户满意度提升有限。'
            },
            {
                'description': '李合作经理带来消息："有一家电商平台想和我们独家合作，提供流量支持，要不要同意？"',
                'dilemma': '独家合作vs多渠道布局',
                'optionA': '签订1年独家合作协议，获得电商平台首页推荐位（价值50万），但不能与其他电商平台合作。',
                'optionB': '拒绝独家协议，投入20万与3家电商平台达成非独家合作，分散风险但单个平台流量支持有限。',
                'impactA': {'money': 0, 'morale': 10, 'market_prospect': 12},
                'impactB': {'money': -20, 'morale': 8, 'market_prospect': 8},
                'feedbackA': '你选择独家合作。短期内获得大量流量，用户增长迅速，但对单一渠道依赖度高，议价能力减弱。',
                'feedbackB': '你选择多渠道布局。虽然单个渠道流量有限，但风险分散，长期发展更加稳健。'
            },
            {
                'description': '张内容运营主管提议："产品内容生态薄弱，我们该做UGC还是PGC？"',
                'dilemma': '内容生态建设方向',
                'optionA': '投入20万设立用户内容激励基金（优质内容奖励50-500元），3个月内培养100名核心UGC创作者，内容丰富但质量难把控。',
                'optionB': '投入35万签约10名行业KOL，每月产出20篇优质PGC内容，质量稳定但内容多样性不足。',
                'impactA': {'money': -20, 'morale': 12, 'market_prospect': 15},
                'impactB': {'money': -35, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择发展UGC。社区活跃度大幅提升，用户粘性增强，但内容质量参差不齐，需要投入大量精力审核。',
                'feedbackB': '你选择签约KOL。内容质量高，品牌调性一致，但用户参与感不强，社区互动不足。'
            },
            {
                'description': '刘客服主管抱怨："用户咨询量日均突破500条，现有3人客服团队根本忙不过来！"',
                'dilemma': '客服体系扩容方案',
                'optionA': '投入24万招聘6名专职客服，培训1个月后上岗，提升响应速度（15分钟内回复）但增加人力成本。',
                'optionB': '投入12万接入智能客服系统，覆盖80%常见咨询，节省成本但复杂问题处理效率低。',
                'impactA': {'money': -24, 'morale': 10, 'market_prospect': 12},
                'impactB': {'money': -12, 'morale': 3, 'market_prospect': 5},
                'feedbackA': '你选择扩充人工客服。用户满意度显著提升，投诉率下降40%，品牌口碑改善。',
                'feedbackB': '你选择智能客服。初期解决了大部分常见问题，但复杂问题处理不当，导致部分用户流失。'
            },
            {
                'description': '王产品总监纠结："团队想加快迭代节奏，是每周小更还是每月大更？"',
                'dilemma': '版本更新频率决策',
                'optionA': '采用"每周小更"模式，投入18万优化研发流程，每周上线1-2个小功能/bug修复，保持用户活跃度但测试压力大。',
                'optionB': '采用"每月大更"模式，投入10万集中资源打磨重大功能，每月上线1个版本，质量更稳定但用户等待周期长。',
                'impactA': {'money': -18, 'morale': 12, 'market_prospect': 8},
                'impactB': {'money': -10, 'morale': 5, 'market_prospect': 10},
                'feedbackA': '你选择每周小更。用户活跃度提升30%，但测试环节偶尔出问题，导致部分更新需要紧急回滚。',
                'feedbackB': '你选择每月大更。版本质量稳定，用户体验一致，但部分用户反馈等待时间过长，期待更多更新频率。'
            }
        ]
        return random.choice(meetings)
    
    def get_late_stage_meeting(self):
        meetings = [
            {
                'description': '李市场副总裁展示区域数据："一线城市用户渗透率达15%，二三线城市仅3%，该怎么扩张？"',
                'dilemma': '市场扩张区域选择',
                'optionA': '投入100万用于二三线城市线下广告（公交/地铁灯箱），为期3个月，快速下沉但获客成本高于一线。',
                'optionB': '继续深耕一线城市，投入80万与5家头部企业达成员工内购合作，提升渗透率至25%但市场天花板临近。',
                'impactA': {'money': -100, 'morale': 12, 'market_prospect': 20},
                'impactB': {'money': -80, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择下沉市场扩张。二三线城市用户量激增，市场份额快速提升，但本地化运营挑战显现，团队压力增大。',
                'feedbackB': '你选择深耕一线城市。企业合作效果显著，ARPU值提升30%，但用户增长开始放缓，市场空间趋于饱和。'
            },
            {
                'description': '张运营总监汇报："用户订单量月增50%，现有团队承接能力不足，该怎么扩容？"',
                'dilemma': '运营团队扩容模式',
                'optionA': '投入80万招聘20名全职运营人员，3个月内完成培训上岗，可控性强但成本高。',
                'optionB': '投入30万与2家外包运营公司合作，按订单量支付服务费（每单抽成5%），灵活但服务质量难保证。',
                'impactA': {'money': -80, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': -50, 'morale': 5, 'market_prospect': 8},
                'feedbackA': '你选择招聘全职人员。团队专业度和执行力显著提升，用户体验一致性保持良好，品牌形象稳固。',
                'feedbackB': '你选择外包合作。短期内解决了人手不足问题，但服务质量参差不齐，用户投诉率上升15%。'
            },
            {
                'description': '王销售总监提议："竞品降价10%抢占市场，我们要不要跟进降价？"',
                'dilemma': '定价策略调整决策',
                'optionA': '产品全线降价15%，预计月销量提升80%，但毛利率从40%降至25%。',
                'optionB': '不降价，投入50万用于品牌宣传（强调技术优势），推出"老用户续费立减30%"活动，保住毛利率但可能流失部分价格敏感用户。',
                'impactA': {'money': 50, 'morale': 12, 'market_prospect': 10},
                'impactB': {'money': -50, 'morale': 8, 'market_prospect': 15},
                'feedbackA': '你选择主动降价。市场份额迅速扩大，用户量突破500万，但利润空间被大幅压缩，长期发展承压。',
                'feedbackB': '你选择差异化竞争。高端用户忠诚度提升，老用户续费率达85%，品牌溢价能力增强，但市场份额小幅下滑。'
            },
            {
                'description': '刘融资顾问带来消息："现有投资方愿意推进A+轮融资，但要求公司先实现盈亏平衡，要不要调整目标？"',
                'dilemma': '融资节奏与盈利目标平衡',
                'optionA': '暂停市场扩张，削减30%营销预算（节省60万），聚焦核心业务提升盈利能力，3个月内实现盈亏平衡，满足融资要求但增长停滞。',
                'optionB': '拒绝调整目标，继续按原计划扩张，放弃A+轮，6个月后再启动融资，保持增长但资金压力加大。',
                'impactA': {'money': 60, 'morale': -5, 'market_prospect': -10},
                'impactB': {'money': -100, 'morale': 10, 'market_prospect': 15},
                'feedbackA': '你选择调整目标实现盈利。成功获得A+轮融资，资金状况改善，但错过市场快速扩张期，竞品趁机崛起。',
                'feedbackB': '你选择坚持扩张。市场领先地位进一步巩固，但资金消耗超出预期，6个月后融资环境恶化，面临更大压力。'
            },
            {
                'description': '李人力总监汇报："公司员工从50人扩至150人，扁平化管理效率越来越低，该怎么调整？"',
                'dilemma': '组织架构优化方向',
                'optionA': '投入40万搭建三层管理架构（部门经理-主管-员工），明确职责分工，提升效率但增加管理层成本。',
                'optionB': '不新增管理层，投入20万引入OKR管理工具，优化协作流程，保持扁平化但可能仍存在沟通内耗。',
                'impactA': {'money': -40, 'morale': 8, 'market_prospect': 12},
                'impactB': {'money': -20, 'morale': 12, 'market_prospect': 8},
                'feedbackA': '你选择建立管理架构。决策链条清晰化，执行力提升，大公司病开始显现但在可控范围内。',
                'feedbackB': '你选择优化扁平管理。团队创新氛围保持良好，但随着规模继续扩大，沟通成本显著增加。'
            },
            {
                'description': '张技术副总裁担忧："现有技术架构支撑30万用户已达极限，用户量再涨就会崩溃！"',
                'dilemma': '技术架构升级方案',
                'optionA': '投入120万进行架构重构，6个月内完成分布式改造，支撑百万级用户但短期影响产品迭代。',
                'optionB': '投入50万进行临时扩容（增加服务器节点），3个月内保障用户量至50万，节省成本但后续仍需重构。',
                'impactA': {'money': -120, 'morale': -5, 'market_prospect': 20},
                'impactB': {'money': -50, 'morale': 8, 'market_prospect': 5},
                'feedbackA': '你选择架构重构。虽然短期内产品更新放缓，但完成后系统性能提升10倍，为未来5年发展奠定基础。',
                'feedbackB': '你选择临时扩容。快速解决了当前问题，但3个月后用户量突破阈值，系统再次面临崩溃风险，被迫紧急重构。'
            },
            {
                'description': '王营销总监提议："现在有两种营销模式，我们该重点投入哪一种？"',
                'dilemma': '营销模式选择',
                'optionA': '投入70万签约2名顶流KOL（粉丝量500万+），拍摄产品测评视频，单条曝光预计100万+但转化效果不确定。',
                'optionB': '投入50万搭建内容营销团队，每月产出30篇行业干货+10条短视频，长期积累流量但短期曝光有限。',
                'impactA': {'money': -70, 'morale': 12, 'market_prospect': 10},
                'impactB': {'money': -50, 'morale': 8, 'market_prospect': 15},
                'feedbackA': '你选择KOL营销。视频发布后话题度激增，新增用户暴增，但粉丝质量参差不齐，留存率偏低。',
                'feedbackB': '你选择内容营销。虽然短期增长不明显，但品牌专业形象建立，用户质量高，6个月后自然增长速度提升3倍。'
            },
            {
                'description': '刘客户成功总监反馈："大客户投诉专属服务不到位，小客户抱怨响应慢，资源该怎么分配？"',
                'dilemma': '客户服务资源倾斜',
                'optionA': '投入50万组建大客户专属服务团队（5人），提供一对一7×24小时服务，保住高价值客户但小客户体验下滑。',
                'optionB': '投入30万优化标准化服务流程，推出自助服务平台，提升小客户响应效率但大客户专属感不足。',
                'impactA': {'money': 80, 'morale': -5, 'market_prospect': 8},
                'impactB': {'money': -30, 'morale': 10, 'market_prospect': 12},
                'feedbackA': '你选择优先服务大客户。大客户续约率提升至95%，贡献收入占比达60%，但小客户流失率上升20%。',
                'feedbackB': '你选择优化标准化服务。整体服务效率提升50%，客户满意度普遍提高，但几位超大型客户因服务不够个性化而流失。'
            },
            {
                'description': '李产品副总裁提议："公司现有核心产品市场份额稳定，要不要拓展新品类？"',
                'dilemma': '产品线扩张决策',
                'optionA': '投入150万组建新品研发团队（10人），8个月内推出衍生产品，开拓新市场但风险高。',
                'optionB': '不拓展新品，投入80万优化现有产品，增加3个核心功能，提升用户复购率但增长空间有限。',
                'impactA': {'money': -150, 'morale': 15, 'market_prospect': 20},
                'impactB': {'money': -80, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择拓展新品类。新产品线成功开拓了新市场，成为公司第二增长曲线，但初期投入大，短期内影响了财务表现。',
                'feedbackB': '你选择深耕现有产品。用户粘性提升，ARPU值增长25%，但市场饱和导致增长趋缓，投资者开始质疑长期发展潜力。'
            },
            {
                'description': '张海外业务负责人带来消息："东南亚市场对我们产品需求强烈，当地没有强势竞品，是否要出海？"',
                'dilemma': '海外市场拓展时机',
                'optionA': '立即出海，投入120万设立新加坡子公司，招募本地团队，6个月内完成本地化上线，抢占先机但风险高。',
                'optionB': '暂缓出海，投入50万与当地代理合作进行小规模测试，验证市场后再决定，稳健但可能错失机会。',
                'impactA': {'money': -120, 'morale': 15, 'market_prospect': 20},
                'impactB': {'money': -50, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择立即出海。成功抢占东南亚市场先机，6个月内用户量突破50万，成为当地领先品牌，但面临文化差异和合规挑战。',
                'feedbackB': '你选择小规模测试。虽然风险可控，但测试期间竞品进入市场并快速扩张，正式进入时已失去先发优势。'
            },
            {
                'description': '王供应链总监汇报："核心零部件依赖单一供应商，最近对方产能紧张，可能断供！"',
                'dilemma': '供应链风险应对',
                'optionA': '投入60万开发2家备用供应商，3个月内完成资质审核和样品测试，分散风险但增加采购成本。',
                'optionB': '与现有供应商签订长期协议，预付40万货款锁定产能，保障供应但资金占用多。',
                'impactA': {'money': -60, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': -40, 'morale': 5, 'market_prospect': 10},
                'feedbackA': '你选择开发备用供应商。成功建立了多元化供应链，虽然短期成本增加，但长期抗风险能力显著提升，避免了潜在的断供危机。',
                'feedbackB': '你选择锁定现有供应商。确保了短期供应稳定，但资金占用增加，且对单一供应商的依赖风险仍然存在。'
            },
            {
                'description': '刘数据总监提议："公司数据量越来越大，但数据分析能力不足，该怎么提升？"',
                'dilemma': '数据分析能力建设',
                'optionA': '投入80万招聘5名数据分析师+采购专业分析工具，6个月内搭建数据驱动体系，自主可控但成本高。',
                'optionB': '投入30万与第三方数据服务公司合作，按需购买分析报告，灵活省钱但数据安全性存疑。',
                'impactA': {'money': -80, 'morale': 12, 'market_prospect': 18},
                'impactB': {'money': -30, 'morale': 5, 'market_prospect': 8},
                'feedbackA': '你选择组建专业团队。成功建立了数据驱动决策体系，业务优化效果显著，多个关键指标提升20%以上。',
                'feedbackB': '你选择第三方合作。短期内解决了数据需求，但随着业务发展，外部依赖和数据安全问题日益凸显。'
            }
        ]
        return random.choice(meetings)
    
    def get_final_stage_meeting(self):
        # 第四阶段：B轮 - 上市/收购窗口期
        meetings = [
            {
                'description': '李投行顾问提醒："上市前需要优化财务报表，要不要通过裁员降本？"',
                'dilemma': '上市筹备与团队稳定平衡',
                'optionA': '裁员15%（主要为非核心部门），节省年度人力成本200万，优化报表但团队士气受挫。',
                'optionB': '不裁员，通过削减营销预算150万+延迟供应商付款周期，优化现金流，保障团队稳定但报表改善效果有限。',
                'impactA': {'money': 200, 'morale': -15, 'market_prospect': 8},
                'impactB': {'money': 150, 'morale': 5, 'market_prospect': 3},
                'feedbackA': '你选择了裁员降本。财务报表显著改善，上市进程加速，但核心员工流失率上升，团队氛围低迷，创新能力受到影响。',
                'feedbackB': '你选择了保护团队。员工忠诚度提升，但财务指标不够亮眼，上市审核过程中遇到了更多问题和质疑。'
            },
            {
                'description': '王投资银行家带来消息："行业巨头提出以3亿估值收购我们，同时上市筹备也在推进，该怎么选？"',
                'dilemma': '收购与独立上市决策',
                'optionA': '接受收购，创始团队获得现金退出（个人收益平均5000万），员工获得3倍薪资补偿，但公司失去独立性。',
                'optionB': '拒绝收购，继续推进上市，预计6个月后IPO（估值预计5亿），潜在收益更高但失败风险（如市场波动）较大。',
                'impactA': {'money': 1000, 'morale': -10, 'market_prospect': -20},
                'impactB': {'money': 500, 'morale': 15, 'market_prospect': 25},
                'feedbackA': '你选择接受收购。创始团队和员工获得了丰厚回报，公司被整合进更大平台，但原有创业文化逐渐消失，部分项目被迫中止。',
                'feedbackB': '你选择独立上市。公司成功IPO，估值达到预期，市场表现强劲，成为行业标杆企业，但也面临更大的业绩压力和监管要求。'
            },
            {
                'description': '刘财务总监汇报："上市前需要调整股权结构，投资方要求增持，员工期权池该怎么处理？"',
                'dilemma': '股权分配调整决策',
                'optionA': '缩减员工期权池从10%至5%，满足投资方增持需求（股权比例提升8%），获得投资方上市资源支持但员工不满。',
                'optionB': '不缩减期权池，引入新战略投资方（出让10%股权），补充上市资金，保障员工权益但原有投资方话语权减弱。',
                'impactA': {'money': 200, 'morale': -10, 'market_prospect': 10},
                'impactB': {'money': 500, 'morale': 10, 'market_prospect': 15},
                'feedbackA': '你选择缩减期权池。获得了现有投资方的全力支持，上市过程顺利，但核心员工流失率上升，内部凝聚力下降。',
                'feedbackB': '你选择引入新投资方。员工权益得到保障，团队稳定性提高，新投资方带来了宝贵的行业资源，但股权结构变得更加复杂。'
            },
            {
                'description': '张技术副总裁提议："上市后需要向投资者展示增长潜力，研发投入该倾向短期还是长期？"',
                'dilemma': '研发投入周期选择',
                'optionA': '投入300万研发短期盈利项目（如广告增值服务），6个月内实现月增收入50万，提升财报数据但长期技术壁垒不足。',
                'optionB': '投入400万研发长期技术储备（如AI大模型适配），12个月内完成，构建核心壁垒但短期无收入贡献。',
                'impactA': {'money': -300, 'morale': 8, 'market_prospect': 10},
                'impactB': {'money': -400, 'morale': 15, 'market_prospect': 25},
                'feedbackA': '你选择短期研发项目。收入增长迅速，股价表现良好，投资者满意度高，但18个月后竞争对手在核心技术上实现突破，市场地位受到挑战。',
                'feedbackB': '你选择长期技术储备。虽然短期内业绩压力较大，但技术壁垒成功建立，2年后成为行业技术领导者，市场份额和估值大幅提升。'
            },
            {
                'description': '李市场副总裁汇报："竞争对手发起价格战，抢占我们10%的市场份额，要不要反击？"',
                'dilemma': '市场份额保卫战策略',
                'optionA': '启动价格战，产品降价20%，投入150万用于补贴，预计3个月内夺回市场份额但毛利率降至15%。',
                'optionB': '不降价，投入200万用于品牌升级+技术专利宣传，强调差异化优势，保住毛利率但市场份额可能继续下滑。',
                'impactA': {'money': -150, 'morale': 10, 'market_prospect': -5},
                'impactB': {'money': -200, 'morale': 15, 'market_prospect': 15},
                'feedbackA': '你选择价格战反击。成功夺回市场份额，但财务状况恶化，投资者信心下降，股价下跌，且行业整体利润水平被拉低。',
                'feedbackB': '你选择差异化竞争。虽然市场份额短期下滑，但高端用户留存率高达90%，利润率保持稳定，品牌溢价能力增强，长期竞争优势明显。'
            },
            {
                'description': '王合规总监提醒："上市前需要完善合规体系，部分业务存在合规风险，该怎么处理？"',
                'dilemma': '合规成本与上市进度平衡',
                'optionA': '投入180万聘请顶级合规团队，3个月内完成所有业务合规整改，无上市风险但成本高。',
                'optionB': '投入80万进行重点业务合规整改，非核心业务暂时维持现状，加快上市进度但可能被监管问询。',
                'impactA': {'money': -180, 'morale': 8, 'market_prospect': 15},
                'impactB': {'money': -80, 'morale': 5, 'market_prospect': -5},
                'feedbackA': '你选择全面合规整改。上市审核顺利通过，公司在投资者中建立了良好信誉，后续监管沟通成本大幅降低。',
                'feedbackB': '你选择重点整改。上市速度加快，但上市后被监管机构重点关注，多次收到问询函，市值波动较大，管理团队疲于应对。'
            },
            {
                'description': '刘战略合作总监带来消息："某行业龙头想与我们达成战略绑定，共享用户数据，要不要同意？"',
                'dilemma': '战略合作与数据独立平衡',
                'optionA': '签订战略绑定协议，共享30%非核心用户数据，获得对方渠道支持（预计年增收入300万），但数据安全风险增加。',
                'optionB': '拒绝数据共享，保持数据独立性，投入120万自建渠道，长期自主可控但短期增长缓慢。',
                'impactA': {'money': 300, 'morale': 8, 'market_prospect': 10},
                'impactB': {'money': -120, 'morale': 12, 'market_prospect': 15},
                'feedbackA': '你选择战略绑定。收入快速增长，但数据共享引发用户隐私担忧，监管审查趋严，未来面临合规风险。',
                'feedbackB': '你选择保持数据独立。虽然增长较慢，但用户信任度提升，在数据隐私法规日益严格的环境中占据了道德高地和合规优势。'
            },
            {
                'description': '李数据商业化负责人提议："公司积累了500万用户数据，要不要进行商业化变现？"',
                'dilemma': '数据变现与隐私保护平衡',
                'optionA': '投入50万搭建数据脱敏处理系统，与3家合规企业合作（如精准营销公司），年变现收入100万但可能引发用户质疑。',
                'optionB': '不进行数据变现，投入80万升级隐私保护技术，强化用户信任但错失收入机会。',
                'impactA': {'money': 50, 'morale': -5, 'market_prospect': 5},
                'impactB': {'money': -80, 'morale': 10, 'market_prospect': 12},
                'feedbackA': '你选择数据变现。获得了新的收入来源，但部分用户发现数据被使用后表达不满，社交媒体负面评价增加，品牌形象受损。',
                'feedbackB': '你选择强化隐私保护。用户忠诚度提升，在隐私保护方面建立了行业领先地位，成为用户信赖的品牌，长期竞争力增强。'
            },
            {
                'description': '张生产总监汇报："上市后预计订单量翻倍，现有产能不足，该怎么扩张？"',
                'dilemma': '产能扩张模式选择',
                'optionA': '投入500万自建工厂（占地10亩），12个月内投产，产能自主可控但固定资产投入大。',
                'optionB': '投入200万与3家代工厂签订长期协议，预付10%货款锁定产能，轻资产模式但交付周期可能延长。',
                'impactA': {'money': -500, 'morale': 10, 'market_prospect': 20},
                'impactB': {'money': -200, 'morale': 5, 'market_prospect': 10},
                'feedbackA': '你选择自建工厂。产能完全自主可控，产品质量和交付时间得到保证，长期成本优势明显，但短期内资金压力较大。',
                'feedbackB': '你选择代工模式。轻资产运营，资金压力小，但多家代工厂的质量一致性难以保证，交付延迟时有发生，客户满意度下降。'
            },
            {
                'description': '王创始人担忧："引入战略投资后，投资方要求派驻3名董事，创始人控制权该怎么保障？"',
                'dilemma': '创始人控制权与融资需求平衡',
                'optionA': '同意投资方派驻董事，放弃部分决策权，获得2亿战略投资，支撑上市后扩张但话语权减弱。',
                'optionB': '拒绝派驻要求，引入小规模战略投资（5000万），创始人保持控股（持股51%），控制权稳定但资金缺口大。',
                'impactA': {'money': 20000, 'morale': -10, 'market_prospect': 15},
                'impactB': {'money': 5000, 'morale': 15, 'market_prospect': 8},
                'feedbackA': '你选择接受投资方董事派驻。获得了充足资金，业务快速扩张，但在战略方向上与投资方产生多次分歧，决策效率下降。',
                'feedbackB': '你选择保持控股。决策自主性强，团队执行力高效，但资金限制导致错失多个重要市场机会，增长速度低于预期。'
            },
            {
                'description': '刘股东代表提议："公司已实现盈利，要不要分红给股东，还是继续投入业务？"',
                'dilemma': '分红与再投资决策',
                'optionA': '拿出年度净利润的30%（约1500万）分红给股东，提升投资方信心但减少业务扩张资金。',
                'optionB': '不分红，将全部净利润（5000万）投入海外市场扩张和技术研发，加速增长但股东短期无收益。',
                'impactA': {'money': -1500, 'morale': 10, 'market_prospect': 5},
                'impactB': {'money': 0, 'morale': -5, 'market_prospect': 20},
                'feedbackA': '你选择分红。股东满意度高，股价短期上涨，但扩张速度放缓，市场份额被竞争对手蚕食，长期发展动力不足。',
                'feedbackB': '你选择全部再投资。业务扩张迅速，市场领导地位巩固，但部分股东对长期不分红表示不满，股价承压，流动性风险增加。'
            },
            {
                'description': '李海外业务副总裁汇报："欧美市场需求旺盛，要不要加大海外投入？"',
                'dilemma': '海外市场扩张模式',
                'optionA': '投入800万在欧美设立2家全资子公司（各10人团队），18个月内完成本地化运营，自主可控但风险高。',
                'optionB': '投入300万与欧美当地分销公司合作，按销售额抽成20%，低成本快速切入但利润空间有限。',
                'impactA': {'money': -800, 'morale': 15, 'market_prospect': 25},
                'impactB': {'money': -300, 'morale': 8, 'market_prospect': 10},
                'feedbackA': '你选择设立全资子公司。虽然前期投入大，挑战多，但成功建立了海外业务体系，品牌国际影响力提升，3年后海外收入占比达35%。',
                'feedbackB': '你选择分销合作。快速进入海外市场，但品牌控制力弱，分销渠道对利润的侵蚀严重，长期增长潜力有限。'
            },
            {
                'description': '张专利负责人汇报："核心技术专利即将到期，要不要通过收购补充专利池？"',
                'dilemma': '专利布局策略',
                'optionA': '投入600万收购2家拥有相关专利的初创公司，快速补充15项核心专利，支撑上市估值但现金消耗大。',
                'optionB': '投入200万组建专利研发团队（8人），24个月内自主申请10项新专利，成本低但周期长。',
                'impactA': {'money': -600, 'morale': 10, 'market_prospect': 15},
                'impactB': {'money': -200, 'morale': 12, 'market_prospect': 8},
                'feedbackA': '你选择收购补充专利。专利壁垒迅速加强，上市估值得到支撑，避免了潜在的专利诉讼风险，但整合难度高于预期。',
                'feedbackB': '你选择自主研发专利。培养了核心研发能力，专利质量高，但上市前专利池规模不足，估值被低估，且面临更多竞争压力。'
            },
            {
                'description': '王投行顾问分析："当前A股和港股都符合上市条件，该选择哪个市场？"',
                'dilemma': '上市地点选择',
                'optionA': '选择A股上市，投入300万用于IPO辅导和合规整改，估值倍数高（约20倍）但审核周期长（12个月）。',
                'optionB': '选择港股上市，投入200万用于上市筹备，审核周期短（6个月）但估值倍数低（约15倍）。',
                'impactA': {'money': -300, 'morale': 10, 'market_prospect': 20},
                'impactB': {'money': -200, 'morale': 15, 'market_prospect': 15},
                'feedbackA': '你选择A股上市。虽然等待时间长，但上市后估值表现优异，再融资能力强，国内品牌影响力大幅提升。',
                'feedbackB': '你选择港股上市。快速完成上市，资金及时到位，但估值低于预期，且面临更大的国际化竞争压力和监管挑战。'
            },
            {
                'description': '刘并购总监提议："上市后需要快速扩大规模，要不要通过收购同行？"',
                'dilemma': '并购与自建团队决策',
                'optionA': '投入1.2亿收购2家区域同行公司，3个月内完成整合，快速提升市场份额但整合风险高。',
                'optionB': '不收购，投入500万在空白区域自建团队（每个区域15人），18个月内完成布局，风险低但速度慢。',
                'impactA': {'money': -12000, 'morale': 8, 'market_prospect': 20},
                'impactB': {'money': -500, 'morale': 12, 'market_prospect': 10},
                'feedbackA': '你选择并购扩张。市场份额迅速提升，但文化整合困难，核心员工流失严重，客户投诉率上升，短期业绩承压。',
                'feedbackB': '你选择自建团队。虽然速度慢，但团队文化一致，服务质量稳定，长期盈利能力强，市场份额稳步提升。'
            },
            {
                'description': '李财务总监提醒："上市后资金需求大，要不要通过债务融资补充现金流？"',
                'dilemma': '债务融资与股权稀释平衡',
                'optionA': '向银行申请3亿授信额度，年利率5%，期限3年，补充现金流但增加财务成本。',
                'optionB': '不进行债务融资，通过增发10%股权融资2.5亿，无利息压力但股东股权被稀释。',
                'impactA': {'money': 30000, 'morale': 5, 'market_prospect': 10},
                'impactB': {'money': 25000, 'morale': -8, 'market_prospect': 15},
                'feedbackA': '你选择债务融资。保持了股权结构稳定，财务杠杆提升了股东回报率，但利息支出成为固定负担，在行业下行期面临更大压力。',
                'feedbackB': '你选择股权融资。无财务压力，资本结构稳健，但现有股东权益被稀释，创始团队控制力进一步减弱，投资者对高估值增发存在争议。'
            }
        ]
        return random.choice(meetings)
        
    def get_post_ipo_stage_meeting(self):
        # 第五阶段：上市后/稳定发展期
        meetings = [
            {
                'description': '王董事会主席提议："上市后股价稳定，要不要启动员工持股计划？"',
                'dilemma': '员工激励与股东权益平衡',
                'optionA': '投入800万从二级市场回购2%股份，用于员工持股计划，提升团队凝聚力但股东权益稀释。',
                'optionB': '不回购股份，推出虚拟股权计划（无实际股份），按年度净利润的5%分红给员工，节省资金但激励效果有限。',
                'impactA': {'money': -800, 'morale': 20, 'market_prospect': 10},
                'impactB': {'money': -500, 'morale': 10, 'market_prospect': 5},
                'feedbackA': '你选择回购股份。员工持股计划极大提升了团队凝聚力和忠诚度，核心人才流失率降至1%以下，创新活力显著增强。',
                'feedbackB': '你选择虚拟股权。节省了大量资金，但虚拟股权的激励效果不及实股，核心人才流失率上升，部分重要项目进展受阻。'
            },
            {
                'description': '李产品总裁汇报："现有产品市场饱和，要不要跨界进入新领域？"',
                'dilemma': '跨界扩张决策',
                'optionA': '投入1.5亿组建跨界研发团队（30人），24个月内推出新领域产品，开拓增长空间但风险极高。',
                'optionB': '不跨界，投入800万优化现有产品生态，提升用户终身价值（LTV），稳健发展但增长天花板明显。',
                'impactA': {'money': -15000, 'morale': 15, 'market_prospect': 25},
                'impactB': {'money': -800, 'morale': 8, 'market_prospect': 5},
                'feedbackA': '你选择跨界扩张。虽然前期投入巨大，遇到重重挑战，但最终成功进入新领域，开辟了第二增长曲线，市值翻倍。',
                'feedbackB': '你选择深耕现有生态。业务稳健，现金流充裕，但增长持续放缓，市盈率下降，投资者开始寻找新的增长点。'
            },
            {
                'description': '张海外合规总监提醒："欧美出台新数据隐私法规，产品需要合规改造，要不要投入？"',
                'dilemma': '海外合规与市场退出决策',
                'optionA': '投入300万进行产品合规改造，6个月内满足新法规要求，保住欧美市场但成本高。',
                'optionB': '不投入合规改造，退出欧美市场，聚焦国内+东南亚市场，节省成本但损失15%的营收。',
                'impactA': {'money': -300, 'morale': 5, 'market_prospect': 15},
                'impactB': {'money': -1500, 'morale': -10, 'market_prospect': -10},
                'feedbackA': '你选择合规改造。成功适应了新法规要求，欧美市场份额保持稳定，在合规方面建立了行业领先地位，增强了品牌信任度。',
                'feedbackB': '你选择退出欧美市场。短期内节省了成本，但失去了重要的增长市场，国际影响力下降，投资者质疑全球化战略。'
            },
            {
                'description': '刘投资者关系总监反馈："机构投资者质疑公司创新能力，要不要加大研发投入？"',
                'dilemma': '研发投入与短期盈利平衡',
                'optionA': '将研发投入占比从10%提升至20%（年增投入1亿），聚焦前沿技术研发，提升投资者信心但短期净利润下滑。',
                'optionB': '维持现有研发投入占比，投入5000万用于市场宣传和投资者沟通，强调现有业务稳定性但创新质疑难消除。',
                'impactA': {'money': -10000, 'morale': 15, 'market_prospect': 20},
                'impactB': {'money': -5000, 'morale': 8, 'market_prospect': 5},
                'feedbackA': '你选择加大研发投入。虽然短期利润下滑，但18个月后多项技术突破带来产品创新，市场反响热烈，股价强势反弹并创新高。',
                'feedbackB': '你选择加强投资者沟通。短期股价企稳，但长期创新不足导致产品竞争力下降，市场份额被蚕食，最终股价持续下跌。'
            },
            {
                'description': '李供应链总裁汇报："全球供应链紧张，核心原材料价格上涨30%，该怎么应对？"',
                'dilemma': '原材料成本上涨应对',
                'optionA': '与供应商签订3年长期协议，预付20%货款锁定价格，稳定成本但占用大量资金。',
                'optionB': '不签订长期协议，投入200万研发替代原材料，6个月内完成测试，降低依赖但短期成本压力大。',
                'impactA': {'money': -2000, 'morale': 10, 'market_prospect': 10},
                'impactB': {'money': -200, 'morale': 12, 'market_prospect': 15},
                'feedbackA': '你选择锁定价格。原材料成本得到有效控制，产品定价策略稳定，客户满意度保持高位，但大量资金被占用，影响了其他投资机会。',
                'feedbackB': '你选择研发替代材料。成功开发出成本更低的替代方案，不仅解决了当前危机，还建立了新的成本优势，提升了长期竞争力。'
            },
            {
                'description': '王品牌总监提议："上市后品牌影响力不足，要不要请国际巨星代言？"',
                'dilemma': '品牌升级策略',
                'optionA': '投入800万邀请国际巨星代言（1年合约），拍摄全球广告片，提升品牌调性但ROI不确定。',
                'optionB': '不请巨星代言，投入300万与行业顶级赛事合作（如世界杯赞助），精准触达目标用户，成本低但曝光量有限。',
                'impactA': {'money': -800, 'morale': 15, 'market_prospect': 12},
                'impactB': {'money': -300, 'morale': 8, 'market_prospect': 8},
                'feedbackA': '你选择国际巨星代言。品牌知名度迅速提升，高端形象树立，国际市场拓展顺利，但代言效果与投入不成正比，ROI仅达到预期的60%。',
                'feedbackB': '你选择赛事合作。精准触达了目标用户群体，品牌专业形象强化，投入产出比优秀，但整体品牌声量增长有限，国际影响力提升缓慢。'
            },
            {
                'description': '刘ESG负责人提议："监管要求上市公司披露ESG报告，要不要加大ESG投入？"',
                'dilemma': 'ESG投入与财务表现平衡',
                'optionA': '投入500万用于环保改造（如绿色工厂）+公益项目，提升ESG评级，满足监管要求但短期无财务回报。',
                'optionB': '投入100万用于基础ESG合规（如数据披露系统），勉强满足监管要求，节省资金但可能被投资者诟病。',
                'impactA': {'money': -500, 'morale': 12, 'market_prospect': 15},
                'impactB': {'money': -100, 'morale': 5, 'market_prospect': -5},
                'feedbackA': '你选择加大ESG投入。ESG评级提升至A级，吸引了大量ESG投资基金，股价上涨15%，员工自豪感增强，品牌价值提升。',
                'feedbackB': '你选择基础合规。虽然节省了资金，但ESG评级仅为C级，被多家机构投资者列入负面观察名单，融资成本上升，国际合作受阻。'
            },
            {
                'description': '李创始人思考："公司已稳定发展，要不要引入职业经理人团队，创始人退居幕后？"',
                'dilemma': '创始人角色转型决策',
                'optionA': '投入1000万聘请国际顶尖职业经理人团队（CEO+COO+CFO），创始人担任董事长，专注战略但失去日常管理权。',
                'optionB': '不引入职业经理人，创始人继续担任CEO，投入500万培养内部管理团队，保持控制权但管理效率可能不足。',
                'impactA': {'money': -1000, 'morale': 10, 'market_prospect': 20},
                'impactB': {'money': -500, 'morale': 15, 'market_prospect': 10},
                'feedbackA': '你选择引入职业经理人。公司治理结构更加规范，管理效率提升，国际化进程加速，但与创始团队在企业文化方面产生了一定冲突。',
                'feedbackB': '你选择培养内部团队。团队凝聚力强，创业文化得以延续，但管理专业化程度不足，在处理复杂国际业务时效率低下，错失部分市场机会。'
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