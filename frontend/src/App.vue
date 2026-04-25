<template>
  <el-container style="min-height: 100vh">
    <!-- Sidebar -->
    <el-aside width="320px" style="background: #f5f7fa; border-right: 1px solid #e4e7ed; padding: 20px; overflow-y: auto;">
      <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #303133; margin: 0; font-size: 18px;">考勤工资计算系统</h2>
        <p style="color: #909399; font-size: 12px; margin-top: 4px;">创新智成-西安东站项目</p>
      </div>

      <FileUploadPanel />
      <ConfigPanel />

      <div style="margin-top: 20px;">
        <el-button
          type="primary"
          :loading="store.calculating"
          :disabled="!store.allUploaded || store.calculated"
          @click="store.calculate()"
          style="width: 100%;"
          size="large"
        >
          <el-icon><CaretRight /></el-icon>
          {{ store.calculating ? '计算中...' : '开始计算' }}
        </el-button>

        <el-button
          v-if="store.calculated"
          @click="store.reset()"
          style="width: 100%; margin-top: 10px;"
          size="large"
        >
          <el-icon><RefreshRight /></el-icon>
          重置
        </el-button>
      </div>

      <el-alert
        v-if="store.error"
        :title="store.error"
        type="error"
        show-icon
        :closable="false"
        style="margin-top: 12px;"
      />
    </el-aside>

    <!-- Main content -->
    <el-main style="padding: 20px 30px; background: #fff; overflow-y: auto;">
      <!-- Empty state -->
      <div v-if="!store.calculated" style="text-align: center; padding: 60px 20px;">
        <el-icon :size="64" color="#c0c4cc"><UploadFilled /></el-icon>
        <h3 style="color: #909399; margin-top: 20px;">请在左侧上传数据文件</h3>
        <el-card style="max-width: 700px; margin: 30px auto; text-align: left;">
          <template #header><strong>使用说明</strong></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="1. 花名册">劳务人员花名册 (.xlsx)，需含"班组花名册"sheet</el-descriptions-item>
            <el-descriptions-item label="2. 考勤记录">员工刷卡记录表 (.xls/.xlsx)，可多选</el-descriptions-item>
            <el-descriptions-item label="3. 工资台账">现有工资台账 (.xlsx)，系统将新增Sheet</el-descriptions-item>
          </el-descriptions>
          <div style="margin-top: 16px; color: #606266; font-size: 13px;">
            <p><strong>计算规则：</strong></p>
            <ul style="padding-left: 20px; line-height: 2;">
              <li>排除工种：管理、安全员、资料员、技术员等</li>
              <li>每日仅一次打卡视为异常，不计入报表</li>
              <li>早班进位：打卡时间 &le; 07:40 按 07:30 计算</li>
              <li>晚班补齐：距整点/半点 &le; {{ store.lateTolerance }}分钟则补齐</li>
              <li>工时取整：按半小时向下取整</li>
              <li>加班分界：16:30 后算加班</li>
            </ul>
          </div>
        </el-card>
      </div>

      <!-- Results -->
      <template v-else>
        <AlertBanner />
        <OverviewCards />
        <JobCharts />
        <SalaryTable />
        <DailyAttendance />
        <DownloadPanel />
      </template>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'
import FileUploadPanel from '@/components/FileUploadPanel.vue'
import ConfigPanel from '@/components/ConfigPanel.vue'
import AlertBanner from '@/components/AlertBanner.vue'
import OverviewCards from '@/components/OverviewCards.vue'
import JobCharts from '@/components/JobCharts.vue'
import SalaryTable from '@/components/SalaryTable.vue'
import DailyAttendance from '@/components/DailyAttendance.vue'
import DownloadPanel from '@/components/DownloadPanel.vue'

const store = useAttendanceStore()

onMounted(async () => {
  const savedId = localStorage.getItem('session_id')
  if (savedId) {
    store.sessionId = savedId
    await store.refreshStatus()
    if (!store.uploadStatus.roster && !store.uploadStatus.attendance && !store.uploadStatus.ledger) {
      // Session invalid, create new
      localStorage.removeItem('session_id')
      await store.initSession()
    }
  } else {
    await store.initSession()
  }
})
</script>

<style>
body {
  margin: 0;
  font-family: "Helvetica Neue", Helvetica, "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "微软雅黑", Arial, sans-serif;
}
</style>
