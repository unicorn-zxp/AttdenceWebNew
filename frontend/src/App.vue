<template>
  <div class="app-layout">
    <!-- Sidebar: only visible in calc tab -->
    <!-- Mobile sidebar backdrop -->
    <div
      v-if="activeTab === 'calc' && !sidebarCollapsed"
      class="sidebar-backdrop"
      @click="sidebarCollapsed = true"
    ></div>

    <transition name="sidebar">
      <aside
        v-show="activeTab === 'calc' && !sidebarCollapsed"
        class="sidebar"
      >
        <!-- Brand Header -->
        <div class="sidebar-brand">
          <div class="brand-icon">创</div>
          <div class="brand-text">
            <div class="brand-title">合肥创新智成</div>
            <div class="brand-subtitle">考勤工资管理系统</div>
          </div>
          <button class="sidebar-close-btn" @click="sidebarCollapsed = true">
            <el-icon :size="18"><Fold /></el-icon>
          </button>
        </div>

        <!-- Scrollable Body -->
        <div class="sidebar-body">
          <div class="sidebar-box">
            <FileUploadPanel />
          </div>
          <div class="sidebar-box">
            <ConfigPanel />
          </div>
          <div class="sidebar-box sidebar-box--actions">
            <el-button
              type="primary"
              :loading="store.calculating"
              :disabled="!store.allUploaded || store.calculated"
              @click="store.calculate()"
              class="btn-calculate"
              size="large"
            >
              <el-icon><CaretRight /></el-icon>
              {{ store.calculating ? '计算中...' : '开始计算' }}
            </el-button>

            <el-button
              v-if="store.calculated || store.allUploaded"
              @click="store.reset()"
              class="btn-reset"
              size="large"
            >
              <el-icon><RefreshRight /></el-icon>
              重置
            </el-button>

            <el-alert
              v-if="store.error"
              :title="store.error"
              type="error"
              show-icon
              :closable="false"
              class="sidebar-error"
            />
          </div>
        </div>
      </aside>
    </transition>

    <!-- Main Area -->
    <div class="main-area">
      <!-- Top Bar -->
      <header class="top-bar">
        <!-- Collapse btn: only in calc tab -->
        <button
          v-if="activeTab === 'calc'"
          class="collapse-btn"
          @click="sidebarCollapsed = !sidebarCollapsed"
        >
          <el-icon :size="18">
            <Fold v-if="!sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
        </button>

        <!-- Brand when on dashboard (no sidebar) -->
        <div v-else class="top-bar-brand">
          <div class="brand-icon brand-icon--small">创</div>
          <span class="top-bar-company">合肥创新智成</span>
        </div>

        <!-- Tab Navigation -->
        <div class="top-bar-tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'dashboard' }"
            @click="activeTab = 'dashboard'"
          >
            <el-icon><DataAnalysis /></el-icon>
            数据看板
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'calc' }"
            @click="activeTab = 'calc'"
          >
            <el-icon><EditPen /></el-icon>
            考勤计算
          </button>
        </div>

        <!-- Project Selector -->
        <div class="project-selector">
          <el-dropdown trigger="click" @command="onProjectCommand">
            <button class="project-btn">
              <el-icon :size="16"><OfficeBuilding /></el-icon>
              <span class="project-btn-name">{{ store.activeProject?.name || '选择项目' }}</span>
              <el-icon :size="12" class="project-btn-arrow"><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  v-for="p in store.projects"
                  :key="p.id"
                  :command="`switch-${p.id}`"
                  :class="{ 'is-active': p.id === store.activeProjectId }"
                >
                  {{ p.name }}
                </el-dropdown-item>
                <el-dropdown-item divided command="add">
                  <el-icon><Plus /></el-icon> 新建项目
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>

        <!-- Right status -->
        <div class="top-bar-right">
          <template v-if="activeTab === 'calc'">
            <el-tag v-if="store.calculated" type="success" effect="light" round>
              <el-icon><CircleCheck /></el-icon> 计算完成
            </el-tag>
            <el-tag v-else-if="store.allUploaded" type="warning" effect="light" round>
              <el-icon><Clock /></el-icon> 待计算
            </el-tag>
            <el-tag v-else effect="plain" round>
              <el-icon><Upload /></el-icon> 上传中 {{ uploadProgress }}/3
            </el-tag>
          </template>
          <template v-else>
            <el-tag effect="plain" round>
              {{ store.annualData.length }} 个月数据
            </el-tag>
          </template>

          <!-- Delete project (only if more than 1) -->
          <el-popconfirm
            v-if="store.projects.length > 1"
            title="确定删除此项目及其所有数据？"
            confirm-button-text="删除"
            cancel-button-text="取消"
            @confirm="store.deleteProject(store.activeProjectId)"
          >
            <template #reference>
              <el-button text size="small" type="danger">
                <el-icon><Delete /></el-icon>
              </el-button>
            </template>
          </el-popconfirm>
        </div>
      </header>

      <!-- Content -->
      <div class="content-scroll">
        <!-- Dashboard Tab -->
        <div v-if="activeTab === 'dashboard'" class="dashboard-view">
          <DashboardView />
        </div>

        <!-- Calc Tab -->
        <div v-else>
          <transition name="fade" mode="out-in">
            <!-- Empty State -->
            <div v-if="!store.calculated" key="empty" class="empty-state">
              <div class="flow-guide">
                <div class="flow-guide-header">
                  <svg class="flow-guide-icon" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <rect x="4" y="8" width="40" height="32" rx="6" stroke="#4F46E5" stroke-width="2.5" fill="rgba(79,70,229,0.06)"/>
                    <path d="M24 18V30M18 24H30" stroke="#4F46E5" stroke-width="2.5" stroke-linecap="round"/>
                  </svg>
                  <div>
                    <h2 class="flow-guide-title">上传数据文件，开始计算</h2>
                    <p class="flow-guide-desc">请点击顶部 ≡ 按钮打开侧边栏，依次上传三个文件，然后点击「开始计算」</p>
                  </div>
                </div>

                <div class="step-cards">
                  <div class="step-card" :class="{ active: store.uploadStatus.roster, done: store.uploadStatus.roster }">
                    <div class="step-number" :class="{ done: store.uploadStatus.roster }">
                      <el-icon v-if="store.uploadStatus.roster"><Check /></el-icon>
                      <span v-else>1</span>
                    </div>
                    <div class="step-info">
                      <div class="step-label">花名册</div>
                      <div class="step-desc">劳务人员花名册 .xlsx</div>
                    </div>
                    <el-icon v-if="store.uploadStatus.roster" class="step-check"><CircleCheckFilled /></el-icon>
                  </div>

                  <div class="step-connector" :class="{ active: store.uploadStatus.roster }"></div>

                  <div class="step-card" :class="{ active: store.uploadStatus.attendance, done: store.uploadStatus.attendance }">
                    <div class="step-number" :class="{ done: store.uploadStatus.attendance }">
                      <el-icon v-if="store.uploadStatus.attendance"><Check /></el-icon>
                      <span v-else>2</span>
                    </div>
                    <div class="step-info">
                      <div class="step-label">考勤记录</div>
                      <div class="step-desc">员工刷卡记录 .xls/.xlsx</div>
                    </div>
                    <el-icon v-if="store.uploadStatus.attendance" class="step-check"><CircleCheckFilled /></el-icon>
                  </div>

                  <div class="step-connector" :class="{ active: store.uploadStatus.attendance }"></div>

                  <div class="step-card" :class="{ active: store.uploadStatus.ledger, done: store.uploadStatus.ledger }">
                    <div class="step-number" :class="{ done: store.uploadStatus.ledger }">
                      <el-icon v-if="store.uploadStatus.ledger"><Check /></el-icon>
                      <span v-else>3</span>
                    </div>
                    <div class="step-info">
                      <div class="step-label">工资台账</div>
                      <div class="step-desc">现有工资台账 .xlsx</div>
                    </div>
                    <el-icon v-if="store.uploadStatus.ledger" class="step-check"><CircleCheckFilled /></el-icon>
                  </div>
                </div>
              </div>

              <el-collapse class="rules-collapse">
                <el-collapse-item title="计算规则说明">
                  <div class="rules-list">
                    <div class="rule-item"><span class="rule-dot"></span>排除工种：管理、安全员、资料员、技术员等</div>
                    <div class="rule-item"><span class="rule-dot"></span>每日仅一次打卡视为异常，不计入报表</div>
                    <div class="rule-item"><span class="rule-dot"></span>早班进位：打卡时间 &le; 07:40 按 07:30 计算</div>
                    <div class="rule-item"><span class="rule-dot"></span>晚班补齐：距整点/半点 &le; {{ store.lateTolerance }}分钟则补齐</div>
                    <div class="rule-item"><span class="rule-dot"></span>工时取整：按半小时向下取整</div>
                    <div class="rule-item"><span class="rule-dot"></span>加班分界：16:30 后算加班</div>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>

            <!-- Results -->
            <div v-else key="results" class="results-container">
              <AlertBanner />
              <OverviewCards />
              <JobCharts />
              <SalaryTable />
              <DailyAttendance />
              <DownloadPanel />
            </div>
          </transition>
        </div>
      </div>
    </div>

    <!-- Add Project Dialog -->
    <el-dialog v-model="showAddProject" title="新建项目" width="400px" :close-on-click-modal="false">
      <div class="add-project-input">
        <el-input
          v-model="newProjectName"
          placeholder="输入项目名称，如：西安北站"
          @keyup.enter="confirmAddProject"
        />
        <el-button type="primary" @click="confirmAddProject" :disabled="!newProjectName.trim()">
          创建
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'
import FileUploadPanel from '@/components/FileUploadPanel.vue'
import ConfigPanel from '@/components/ConfigPanel.vue'
import AlertBanner from '@/components/AlertBanner.vue'
import OverviewCards from '@/components/OverviewCards.vue'
import DashboardView from '@/components/DashboardView.vue'
import JobCharts from '@/components/JobCharts.vue'
import SalaryTable from '@/components/SalaryTable.vue'
import DailyAttendance from '@/components/DailyAttendance.vue'
import DownloadPanel from '@/components/DownloadPanel.vue'

const store = useAttendanceStore()
const sidebarCollapsed = ref(false)
const activeTab = ref<'dashboard' | 'calc'>('dashboard')
const showAddProject = ref(false)
const newProjectName = ref('')

async function onProjectCommand(cmd: string) {
  if (cmd === 'add') {
    showAddProject.value = true
    return
  }
  if (cmd.startsWith('switch-')) {
    const id = Number(cmd.replace('switch-', ''))
    if (id !== store.activeProjectId) {
      await store.switchProject(id)
    }
  }
}

async function confirmAddProject() {
  if (!newProjectName.value.trim()) return
  await store.createProject(newProjectName.value.trim())
  newProjectName.value = ''
  showAddProject.value = false
}

// Switch to calc tab after calculation completes
watch(() => store.calculated, (val) => {
  if (val) activeTab.value = 'calc'
})

const uploadProgress = computed(() => {
  let count = 0
  if (store.uploadStatus.roster) count++
  if (store.uploadStatus.attendance) count++
  if (store.uploadStatus.ledger) count++
  return count
})

onMounted(async () => {
  await store.fetchProjects()
  store.fetchAnnual()
  const savedId = localStorage.getItem('session_id')
  if (savedId) {
    store.sessionId = savedId
    await store.refreshStatus()
    if (!store.uploadStatus.roster && !store.uploadStatus.attendance && !store.uploadStatus.ledger) {
      localStorage.removeItem('session_id')
      await store.initSession()
    }
  } else {
    await store.initSession()
  }
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
}

/* ===== Sidebar ===== */
.sidebar {
  width: var(--sidebar-width);
  min-width: var(--sidebar-width);
  background: var(--color-sidebar);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
  z-index: 10;
}
.sidebar-enter-active,
.sidebar-leave-active {
  transition: width var(--transition-base), min-width var(--transition-base), opacity var(--transition-fast);
}
.sidebar-enter-from,
.sidebar-leave-to {
  width: 0;
  min-width: 0;
  opacity: 0;
}

.sidebar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.brand-icon {
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--color-brand);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: var(--text-lg);
  flex-shrink: 0;
}
.brand-icon--small {
  width: 28px;
  height: 28px;
  font-size: var(--text-base);
  border-radius: var(--radius-sm);
}
.brand-title {
  color: var(--color-text-inverse);
  font-size: var(--text-md);
  font-weight: 600;
  line-height: 1.3;
}
.brand-subtitle {
  color: var(--color-text-inverse-secondary);
  font-size: var(--text-xs);
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-4) var(--space-5);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}
.sidebar-body::-webkit-scrollbar {
  width: 4px;
}
.sidebar-body::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.15);
  border-radius: 2px;
}

.sidebar-box {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-lg);
  padding: var(--space-4) var(--space-4);
}
.sidebar-box--actions {
  background: rgba(255,255,255,0.02);
  border-color: rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.btn-calculate {
  width: 100%;
}
.btn-reset {
  width: 100%;
  margin-top: var(--space-2);
  margin-left: 0 !important;
  background: rgba(255,255,255,0.08) !important;
  border-color: rgba(255,255,255,0.15) !important;
  color: var(--color-text-inverse-secondary) !important;
}
.btn-reset:hover {
  background: rgba(255,255,255,0.14) !important;
}
.sidebar-error {
  margin-top: var(--space-3);
}

/* ===== Main Area ===== */
.main-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  background: var(--color-bg);
}

/* ===== Top Bar ===== */
.top-bar {
  height: var(--header-height);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: 0 var(--space-6);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}
.collapse-btn {
  width: 36px;
  height: 36px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}
.collapse-btn:hover {
  background: var(--color-bg);
  color: var(--color-text-primary);
}
.top-bar-brand {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.top-bar-company {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
  white-space: nowrap;
}

/* ===== Tab Navigation ===== */
.top-bar-tabs {
  display: flex;
  gap: 0;
  background: var(--color-bg);
  border-radius: var(--radius-lg);
  padding: 4px;
  border: 1px solid var(--color-border-light);
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 22px;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-base);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
  position: relative;
}
.tab-btn .el-icon {
  font-size: 18px;
}
.tab-btn:hover {
  color: var(--color-text-secondary);
}
.tab-btn.active {
  background: var(--color-brand);
  color: white;
  box-shadow: 0 2px 8px rgba(79, 70, 229, 0.3);
}

.top-bar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

/* ===== Project Selector ===== */
.project-selector {
  display: flex;
  align-items: center;
}
.project-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  cursor: pointer;
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
}
.project-btn:hover {
  border-color: var(--color-brand);
  color: var(--color-brand);
}
.project-btn-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.project-btn-arrow {
  color: var(--color-text-tertiary);
}

/* Add project dialog */
.add-project-input {
  display: flex;
  gap: var(--space-2);
  align-items: center;
  padding: var(--space-3);
}

/* ===== Content Scroll ===== */
.content-scroll {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-6);
}

.dashboard-view {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.results-container {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

/* ===== Empty State ===== */
.empty-state {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--space-8) 0;
}

/* Flow Guide Card */
.flow-guide {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--space-5);
}
.flow-guide-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  margin-bottom: var(--space-5);
}
.flow-guide-icon {
  width: 48px;
  height: 48px;
  flex-shrink: 0;
}
.flow-guide-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-1) 0;
}
.flow-guide-desc {
  color: var(--color-text-tertiary);
  margin: 0;
  font-size: var(--text-sm);
}

/* Step Cards */
.step-cards {
  display: flex;
  align-items: center;
  gap: 0;
}
.step-card {
  flex: 1;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  transition: all var(--transition-fast);
}
.step-card.done {
  border-color: var(--color-success);
  background: var(--color-success-light);
}
.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-tertiary);
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.step-number.done {
  background: var(--color-success);
  border-color: var(--color-success);
  color: white;
}
.step-info {
  flex: 1;
  min-width: 0;
}
.step-label {
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--color-text-primary);
}
.step-desc {
  font-size: var(--text-xs);
  color: var(--color-text-tertiary);
  margin-top: 2px;
}
.step-check {
  color: var(--color-success);
  font-size: 20px;
  flex-shrink: 0;
}

.step-connector {
  width: 24px;
  height: 2px;
  background: var(--color-border);
  flex-shrink: 0;
  transition: background var(--transition-fast);
}
.step-connector.active {
  background: var(--color-success);
}

/* Rules */
.rules-collapse :deep(.el-collapse-item__header) {
  font-weight: 600;
  color: var(--color-text-secondary);
}
.rules-list {
  line-height: 2;
}
.rule-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
}
.rule-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--color-text-tertiary);
  flex-shrink: 0;
}

/* ===== Responsive ===== */

/* Mobile sidebar backdrop */
.sidebar-backdrop {
  display: none;
}

.sidebar-close-btn {
  display: none;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-sm);
  background: rgba(255,255,255,0.08);
  color: var(--color-text-inverse-secondary);
  cursor: pointer;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  flex-shrink: 0;
  transition: all var(--transition-fast);
}
.sidebar-close-btn:hover {
  background: rgba(255,255,255,0.15);
  color: var(--color-text-inverse);
}

@media (max-width: 1024px) {
  .sidebar {
    position: fixed;
    top: 0;
    right: 0;
    left: auto;
    height: 100vh;
    width: 300px !important;
    min-width: 300px !important;
    z-index: 100;
    box-shadow: var(--shadow-lg);
  }
  .sidebar-close-btn {
    display: flex;
  }
  .sidebar-backdrop {
    display: block;
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 99;
  }
  .step-cards {
    flex-direction: column;
    gap: var(--space-2);
  }
  .step-connector {
    width: 2px;
    height: 16px;
  }
  .flow-guide {
    padding: var(--space-4);
  }
  .flow-guide-header {
    flex-direction: column;
    gap: var(--space-2);
    text-align: center;
  }
  .flow-guide-icon {
    width: 40px;
    height: 40px;
  }
}

@media (max-width: 640px) {
  .top-bar {
    padding: 0 var(--space-3);
    gap: var(--space-2);
  }
  .tab-btn {
    padding: 6px 12px;
    gap: 4px;
    font-size: var(--text-sm);
  }
  .tab-btn .el-icon {
    font-size: 14px;
  }
  .project-btn-name {
    max-width: 72px;
  }
  .top-bar-right :deep(.el-tag) {
    font-size: 11px;
    padding: 0 6px;
    height: 22px;
  }
  .content-scroll {
    padding: var(--space-3);
  }
  .empty-state {
    padding: var(--space-4) 0;
  }
  .step-card {
    padding: var(--space-3);
  }
  .step-desc {
    display: none;
  }
}
</style>
