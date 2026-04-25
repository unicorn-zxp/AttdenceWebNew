<template>
  <el-card shadow="hover" style="margin-bottom: 20px;">
    <template #header><strong>下载结果</strong></template>
    <el-row :gutter="16">
      <el-col :span="8">
        <el-button type="primary" @click="download('attendance-summary')" style="width: 100%;">
          <el-icon><Document /></el-icon>
          考勤记录汇总
        </el-button>
      </el-col>
      <el-col :span="8">
        <el-button type="success" @click="download('ledger')" style="width: 100%;">
          <el-icon><Notebook /></el-icon>
          工资台账（含新增Sheet）
        </el-button>
      </el-col>
      <el-col :span="8">
        <el-button type="warning" @click="download('report')" style="width: 100%;">
          <el-icon><Tickets /></el-icon>
          上报表
        </el-button>
      </el-col>
    </el-row>
    <el-alert
      v-if="store.sheetName"
      type="info"
      :closable="false"
      style="margin-top: 12px;"
    >
      工资台账已新增Sheet: <strong>{{ store.sheetName }}</strong>
    </el-alert>
  </el-card>
</template>

<script setup lang="ts">
import { ElMessage } from 'element-plus'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()

function download(type: string) {
  const url = store.getDownloadUrl(type)
  const link = document.createElement('a')
  link.href = url
  link.click()
  ElMessage.success('开始下载')
}
</script>
