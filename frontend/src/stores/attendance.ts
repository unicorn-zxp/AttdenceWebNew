import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import client from '@/api/client'
import type {
  SalaryRecord,
  DailyRecord,
  OverviewStats,
  UploadStatus,
  CalculateResponse,
} from '@/types'

export const useAttendanceStore = defineStore('attendance', () => {
  // State
  const sessionId = ref<string>('')
  const uploadStatus = ref<UploadStatus>({
    roster: false,
    attendance: false,
    ledger: false,
    attendance_count: 0,
  })
  const calculating = ref(false)
  const calculated = ref(false)
  const overview = ref<OverviewStats>({
    total_people: 0,
    total_salary: 0,
    total_workdays: 0,
    total_overtime: 0,
  })
  const salaryData = ref<SalaryRecord[]>([])
  const dailyData = ref<DailyRecord[]>([])
  const sheetName = ref('')
  const abnormalCount = ref(0)
  const lateTolerance = ref(10)
  const error = ref('')

  // Computed
  const allUploaded = computed(
    () => uploadStatus.value.roster && uploadStatus.value.attendance && uploadStatus.value.ledger,
  )

  const abnormalRecords = computed(() =>
    salaryData.value.filter((r) => r.备注 && r.备注 !== ''),
  )

  // Actions
  async function initSession() {
    try {
      const { data } = await client.post('/session')
      sessionId.value = data.session_id
      localStorage.setItem('session_id', data.session_id)
    } catch (e: any) {
      error.value = e.message
    }
  }

  async function refreshStatus() {
    if (!sessionId.value) return
    try {
      const { data } = await client.get('/upload/status')
      uploadStatus.value = data
    } catch {
      // session might not exist, ignore
    }
  }

  async function uploadRoster(file: File) {
    const form = new FormData()
    form.append('file', file)
    await client.post('/upload/roster', form)
    await refreshStatus()
  }

  async function uploadAttendance(files: File[]) {
    const form = new FormData()
    files.forEach((f) => form.append('files', f))
    await client.post('/upload/attendance', form)
    await refreshStatus()
  }

  async function uploadLedger(file: File) {
    const form = new FormData()
    form.append('file', file)
    await client.post('/upload/ledger', form)
    await refreshStatus()
  }

  async function calculate() {
    calculating.value = true
    error.value = ''
    try {
      const { data } = await client.post<CalculateResponse>('/calculate')
      overview.value = data.overview
      sheetName.value = data.sheet_name
      abnormalCount.value = data.abnormal_count
      calculated.value = true
      // Fetch full data
      await fetchResults()
    } catch (e: any) {
      error.value = e.message
    } finally {
      calculating.value = false
    }
  }

  async function fetchResults() {
    const [salaryRes, dailyRes] = await Promise.all([
      client.get('/results/salary'),
      client.get('/results/daily'),
    ])
    salaryData.value = salaryRes.data.records
    dailyData.value = dailyRes.data.records
    overview.value = salaryRes.data.overview
    sheetName.value = salaryRes.data.sheet_name
  }

  async function reset() {
    if (sessionId.value) {
      await client.delete(`/session/${sessionId.value}`)
    }
    sessionId.value = ''
    calculated.value = false
    salaryData.value = []
    dailyData.value = []
    overview.value = { total_people: 0, total_salary: 0, total_workdays: 0, total_overtime: 0 }
    sheetName.value = ''
    abnormalCount.value = 0
    uploadStatus.value = { roster: false, attendance: false, ledger: false, attendance_count: 0 }
    error.value = ''
    localStorage.removeItem('session_id')
    await initSession()
  }

  async function updateConfig(tolerance: number) {
    lateTolerance.value = tolerance
    await client.put('/config', null, { params: { late_tolerance: tolerance } })
  }

  function getDownloadUrl(type: string): string {
    return `/api/download/${type}?session_id=${sessionId.value}`
  }

  return {
    sessionId,
    uploadStatus,
    calculating,
    calculated,
    overview,
    salaryData,
    dailyData,
    sheetName,
    abnormalCount,
    lateTolerance,
    error,
    allUploaded,
    abnormalRecords,
    initSession,
    refreshStatus,
    uploadRoster,
    uploadAttendance,
    uploadLedger,
    calculate,
    fetchResults,
    reset,
    updateConfig,
    getDownloadUrl,
  }
})
