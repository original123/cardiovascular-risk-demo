<template>
  <main class="page-shell">
    <section class="top-band">
      <div>
        <p class="eyebrow">China-PAR 风险评估</p>
        <h1>心血管病风险评估</h1>
      </div>
      <div class="model-note">本 demo 用于规则验证；终生风险为工程拟合近似。</div>
    </section>

    <section class="workspace">
      <form class="panel form-panel" @submit.prevent="submit">
        <div class="panel-title">
          <h2>评估问卷</h2>
          <button class="ghost" type="button" @click="fillGuideSample">填入指南样例</button>
        </div>

        <div class="form-grid">
          <FieldGroup number="01" title="性别">
            <Segmented v-model="form.sex" :options="sexOptions" />
          </FieldGroup>

          <FieldGroup number="02" title="年龄（岁）">
            <input v-model.number="form.age" type="number" min="20" max="85" />
          </FieldGroup>

          <FieldGroup number="03" title="现居住地区">
            <Segmented v-model="form.region" :options="regionOptions" />
            <Segmented v-model="form.area" :options="areaOptions" />
          </FieldGroup>

          <FieldGroup number="04" title="腰围（cm）">
            <input v-model.number="form.waist" type="number" min="50" max="130" step="0.1" />
          </FieldGroup>

          <FieldGroup number="05" title="总胆固醇">
            <Segmented v-model="form.tc_unit" :options="unitOptions" />
            <input
              v-model.number="form.tc"
              type="number"
              :min="form.tc_unit === 1 ? 80 : 2"
              :max="form.tc_unit === 1 ? 400 : 11"
              step="0.01"
              :placeholder="form.tc_unit === 1 ? '80-400' : '2-11'"
            />
          </FieldGroup>

          <FieldGroup number="06" title="高密度脂蛋白胆固醇">
            <Segmented v-model="form.hdlc_unit" :options="unitOptions" />
            <input
              v-model.number="form.hdlc"
              type="number"
              :min="form.hdlc_unit === 1 ? 20 : 0.5"
              :max="form.hdlc_unit === 1 ? 130 : 4"
              step="0.01"
              :placeholder="form.hdlc_unit === 1 ? '20-130' : '0.5-4'"
            />
          </FieldGroup>

          <FieldGroup number="07" title="当前血压水平（mmHg）">
            <div class="inline-inputs">
              <label>收缩压<input v-model.number="form.sbp" type="number" min="70" max="200" /></label>
              <label>舒张压<input v-model.number="form.dbp" type="number" min="40" max="140" /></label>
            </div>
          </FieldGroup>

          <FieldGroup number="08" title="服用降压药">
            <Segmented v-model="form.drug" :options="yesNoOptions" />
          </FieldGroup>

          <FieldGroup number="09" title="患糖尿病">
            <Segmented v-model="form.dm" :options="yesNoOptions" />
          </FieldGroup>

          <FieldGroup number="10" title="现在是否吸烟">
            <Segmented v-model="form.csmoke" :options="yesNoOptions" />
          </FieldGroup>

          <FieldGroup number="11" title="心脑血管病家族史">
            <Segmented v-model="form.fh_ascvd" :options="yesNoOptions" />
          </FieldGroup>
        </div>

        <div v-if="error" class="error-box">{{ error }}</div>
        <button class="submit" type="submit" :disabled="loading">
          {{ loading ? '评估中...' : '提交评估' }}
        </button>
      </form>

      <section class="panel result-panel">
        <div class="panel-title">
          <h2>评估结果</h2>
          <span v-if="result" class="status-pill">已计算</span>
        </div>

        <div v-if="!result" class="empty-state">提交问卷后显示风险值、分层和建议。</div>

        <template v-else>
          <div class="risk-grid">
            <RiskCard title="10年发病风险" :risk="result.tenYearRisk" />
            <RiskCard title="理想10年风险" :risk="result.idealTenYearRisk" muted />
            <RiskCard
              v-if="result.lifetimeRisk"
              title="终生发病风险"
              :risk="result.lifetimeRisk"
            />
            <RiskCard
              v-if="result.idealLifetimeRisk"
              title="理想终生风险"
              :risk="result.idealLifetimeRisk"
              muted
            />
          </div>

          <p v-if="result.lifetimeRiskNote" class="soft-note">{{ result.lifetimeRiskNote }}</p>
          <p class="soft-note">{{ result.models.lifetimeRisk.warning }}</p>

          <div class="advice">
            <h3>温馨建议</h3>
            <ol>
              <li v-for="item in result.advice" :key="item">{{ item }}</li>
            </ol>
          </div>

          <details class="data-details">
            <summary>个人数据</summary>
            <dl>
              <template v-for="item in inputRows" :key="item.label">
                <dt>{{ item.label }}</dt>
                <dd>{{ item.value }}</dd>
              </template>
            </dl>
          </details>
        </template>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, defineComponent, h, reactive, ref } from 'vue'

const API_BASE = import.meta.env.VITE_API_BASE_URL || ''

const sexOptions = [
  { label: '男', value: 1 },
  { label: '女', value: 2 },
]
const regionOptions = [
  { label: '南方', value: 0 },
  { label: '北方', value: 1 },
]
const areaOptions = [
  { label: '农村', value: 0 },
  { label: '城市', value: 1 },
]
const yesNoOptions = [
  { label: '否', value: 0 },
  { label: '是', value: 1 },
]
const unitOptions = [
  { label: 'mg/dl', value: 1 },
  { label: 'mmol/L', value: 2 },
]

const defaultForm = {
  sex: 1,
  age: 40,
  region: 1,
  area: 1,
  waist: 90,
  tc_unit: 1,
  tc: 200,
  hdlc_unit: 1,
  hdlc: 40,
  sbp: 120,
  dbp: 80,
  drug: 0,
  dm: 0,
  csmoke: 0,
  fh_ascvd: 0,
}

const form = reactive({ ...defaultForm })
const result = ref(null)
const error = ref('')
const loading = ref(false)

function fillGuideSample() {
  Object.assign(form, {
    sex: 1,
    age: 40,
    region: 1,
    area: 1,
    waist: 80,
    tc_unit: 2,
    tc: 5.2,
    hdlc_unit: 2,
    hdlc: 1.3,
    sbp: 145,
    dbp: 80,
    drug: 0,
    dm: 0,
    csmoke: 0,
    fh_ascvd: 1,
  })
}

function localValidate() {
  if (form.age < 20 || form.age > 85) return '年龄应在20-85之间'
  if (form.sbp < 70 || form.sbp > 200) return '收缩压应在70-200之间'
  if (form.dbp < 40 || form.dbp > 140) return '舒张压应在40-140之间'
  if (form.waist < 50 || form.waist > 130) return '腰围应在50-130之间'
  return ''
}

async function submit() {
  error.value = localValidate()
  if (error.value) return
  loading.value = true
  result.value = null
  try {
    const response = await fetch(`${API_BASE}/api/risk/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    })
    const data = await response.json()
    if (!response.ok || !data.success) {
      throw new Error(data.message || '评估失败')
    }
    result.value = data.result
  } catch (err) {
    error.value = err.message || '评估失败'
  } finally {
    loading.value = false
  }
}

const inputRows = computed(() => {
  if (!result.value) return []
  const input = result.value.input
  return [
    { label: '性别', value: input.sex === 1 ? '男' : '女' },
    { label: '年龄', value: input.age },
    { label: '现居住地区', value: `${input.region === 1 ? '北方' : '南方'} / ${input.area === 1 ? '城市' : '农村'}` },
    { label: '腰围', value: `${input.waist} cm` },
    { label: '总胆固醇', value: `${input.tc} ${input.tc_unit === 1 ? 'mg/dl' : 'mmol/L'}` },
    { label: 'HDL-C', value: `${input.hdlc} ${input.hdlc_unit === 1 ? 'mg/dl' : 'mmol/L'}` },
    { label: '血压', value: `${input.sbp}/${input.dbp} mmHg` },
    { label: '服用降压药', value: input.drug === 1 ? '是' : '否' },
    { label: '糖尿病', value: input.dm === 1 ? '是' : '否' },
    { label: '吸烟', value: input.csmoke === 1 ? '是' : '否' },
    { label: '家族史', value: input.fh_ascvd === 1 ? '是' : '否' },
  ]
})

const FieldGroup = defineComponent({
  props: { number: String, title: String },
  setup(props, { slots }) {
    return () =>
      h('div', { class: 'field-group' }, [
        h('div', { class: 'field-title' }, [
          h('span', { class: 'field-number' }, props.number),
          h('span', props.title),
        ]),
        h('div', { class: 'field-control' }, slots.default?.()),
      ])
  },
})

const Segmented = defineComponent({
  props: { modelValue: [Number, String], options: Array },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    return () =>
      h(
        'div',
        { class: 'segmented' },
        props.options.map((option) =>
          h(
            'button',
            {
              type: 'button',
              class: { active: props.modelValue === option.value },
              onClick: () => emit('update:modelValue', option.value),
            },
            option.label,
          ),
        ),
      )
  },
})

const RiskCard = defineComponent({
  props: { title: String, risk: Object, muted: Boolean },
  setup(props) {
    return () =>
      h('article', { class: ['risk-card', props.muted ? 'muted' : '', props.risk?.level || ''] }, [
        h('span', { class: 'risk-title' }, props.title),
        h('strong', `${props.risk.percent}%`),
        props.risk.level ? h('em', props.risk.level) : null,
      ])
  },
})
</script>
