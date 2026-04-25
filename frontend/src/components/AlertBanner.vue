<template>
  <el-alert
    v-if="store.abnormalCount > 0"
    type="warning"
    :closable="false"
    style="margin-bottom: 16px;"
  >
    <template #title>
      <span>共 {{ store.abnormalCount }} 人存在异常</span>
    </template>
    <el-table
      :data="store.abnormalRecords"
      size="small"
      stripe
      :max-height="200"
      style="margin-top: 8px;"
    >
      <el-table-column prop="序号" label="序号" width="60" />
      <el-table-column prop="姓名" label="姓名" width="80" />
      <el-table-column prop="工种" label="工种" width="80" />
      <el-table-column prop="出勤工日" label="出勤工日" width="80" />
      <el-table-column prop="加班工时" label="加班工时" width="80" />
      <el-table-column prop="备注" label="备注" />
    </el-table>
  </el-alert>
  <el-alert
    v-else-if="store.calculated"
    type="success"
    title="所有人员均有工资标准，无异常"
    :closable="false"
    style="margin-bottom: 16px;"
  />
</template>

<script setup lang="ts">
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
</script>
