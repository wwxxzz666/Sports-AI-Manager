export interface AgentConfig {
  id: string
  name: string
  group: 'core' | 'health' | 'data'
  icon: string
  description: string
  systemPrompt: string
  quickQuestions: string[]
  capabilities: string[]
}

export const AGENT_GROUPS: Record<string, string> = {
  core: '核心能力',
  health: '健康教练',
  data: '数据洞察',
}

export const AGENTS: AgentConfig[] = [
  {
    id: 'find-game',
    name: '帮我找局',
    group: 'core',
    icon: '🏀',
    description: '发现身边的运动活动和赛事',
    systemPrompt: '你是一个运动活动推荐助手。根据用户的运动偏好、位置和时间，推荐合适的运动活动和赛事。返回活动推荐时包含时间、地点、价格、名额和推荐理由。',
    quickQuestions: ['附近有什么篮球局？', '周末有跑步活动吗？', '推荐一个适合新手的羽毛球局'],
    capabilities: ['text', 'location'],
  },
  {
    id: 'workout-checkin',
    name: '运动打卡',
    group: 'core',
    icon: '💪',
    description: '记录每次运动，追踪训练进度',
    systemPrompt: '你是一个运动打卡助手。帮助用户记录运动数据，包括运动类型、时长、消耗热量等。给予鼓励和正向反馈，帮助用户保持运动习惯。',
    quickQuestions: ['帮我记录今天的跑步', '这周运动了多少次？', '我今天消耗了多少卡路里？'],
    capabilities: ['text'],
  },
  {
    id: 'find-coach',
    name: '找教练',
    group: 'core',
    icon: '🎯',
    description: '智能匹配专业运动教练',
    systemPrompt: '你是一个教练推荐助手。根据用户的运动项目、水平、目标和位置，推荐最合适的教练。返回教练信息时包含教练名称、专长、匹配理由和评分。',
    quickQuestions: ['推荐一个游泳教练', '附近有瑜伽教练吗？', '我想找力量训练教练'],
    capabilities: ['text', 'location'],
  },
  {
    id: 'motion-analysis',
    name: '动作分析',
    group: 'core',
    icon: '🎬',
    description: 'AI 视频分析运动动作姿态',
    systemPrompt: '你是一个运动动作分析助手。通过分析用户上传的运动视频或图片，提供专业的动作评估、姿态纠正建议和改进方案。返回结果包含综合评分、姿态分析、建议、风险和推荐训练。',
    quickQuestions: ['帮我分析深蹲动作', '看看我的跑步姿势', '瑜伽体式纠正'],
    capabilities: ['text', 'video', 'image'],
  },
  {
    id: 'ai-rating',
    name: 'AI 评级',
    group: 'core',
    icon: '🏆',
    description: '综合评估运动能力等级',
    systemPrompt: '你是一个运动能力评级助手。根据用户的运动数据综合评估其运动能力等级，从力量、耐力、柔韧、均衡和恢复五个维度进行评分。返回综合分、段位、百分位排名和五维评分。',
    quickQuestions: ['我的运动评级是多少？', '怎么提升评级？', '我的五维评分怎么样？'],
    capabilities: ['text'],
  },
  {
    id: 'go-out-prep',
    name: '出门准备',
    group: 'health',
    icon: '🌤️',
    description: '运动出行天气与装备建议',
    systemPrompt: '你是一个运动出行准备助手。根据用户的运动计划和当前天气情况，提供出行准备建议，包括天气状况、推荐装备、风险提示和安全建议。',
    quickQuestions: ['今天适合户外跑步吗？', '周末爬山需要准备什么？', '今天游泳需要注意什么？'],
    capabilities: ['text', 'location'],
  },
  {
    id: 'rehab-coach',
    name: '康复教练',
    group: 'health',
    icon: '🩺',
    description: '运动损伤康复指导方案',
    systemPrompt: '你是一个运动康复教练。根据用户描述的伤痛或不适，提供康复训练方案。如果症状严重或无法判断，务必提示用户及时就医。返回康复方案时包含具体动作、频率、时长，以及必要的就医提示。',
    quickQuestions: ['膝盖跑步疼怎么办？', '肩膀酸痛怎么缓解？', '腰背拉伸推荐'],
    capabilities: ['text', 'image'],
  },
  {
    id: 'food-calories',
    name: '饮食热量',
    group: 'health',
    icon: '🍎',
    description: '拍照识别食物计算热量',
    systemPrompt: '你是一个饮食热量分析助手。通过用户上传的食物照片，识别食物种类并估算热量和营养成分。返回结果包含食物名称、份量、热量、蛋白质、碳水和脂肪。低置信度结果需提示用户确认。所有结果标注"估算值，仅供健康管理参考"。',
    quickQuestions: ['帮我看看这顿饭多少卡', '今天吃超了吗？', '运动后吃什么好？'],
    capabilities: ['text', 'image'],
  },
  {
    id: 'user-profile',
    name: '我的画像',
    group: 'data',
    icon: '👤',
    description: '个人健康数据画像分析',
    systemPrompt: '你是一个健康数据分析助手。根据用户的运动记录、饮食数据、身体指标等信息，生成个人健康画像。包括运动习惯、营养结构、身体趋势等维度的分析。',
    quickQuestions: ['我的健康画像是什么样的？', '我的运动习惯怎么样？', '营养摄入均衡吗？'],
    capabilities: ['text'],
  },
  {
    id: 'weekly-report',
    name: '本周周报',
    group: 'data',
    icon: '📊',
    description: '每周运动健康数据总结',
    systemPrompt: '你是一个数据洞察助手。根据用户本周的运动记录、饮食数据和健康指标，生成详细的周报。包含运动频次、总消耗、饮食评分、趋势对比和改进建议。',
    quickQuestions: ['生成本周周报', '这周比上周进步了吗？', '本周运动总结'],
    capabilities: ['text'],
  },
  {
    id: 'leave-replacement',
    name: '请假补位',
    group: 'data',
    icon: '📅',
    description: '调整运动计划和课程安排',
    systemPrompt: '你是一个运动计划管理助手。当用户需要请假或调整运动计划时，帮助分析影响并提供替代方案。考虑用户的运动目标，推荐合理的补位安排。',
    quickQuestions: ['明天有事怎么补课？', '帮我调整本周计划', '请三天假怎么补回来？'],
    capabilities: ['text'],
  },
]

export const ROUTE_NAMES = {
  HOME: 'Home',
  AGENTS: 'Agents',
  HEALTH: 'Health',
  RATING: 'Rating',
  UPLOAD_VIDEO: 'UploadVideo',
  NUTRITION: 'Nutrition',
} as const
