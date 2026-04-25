<template>
  <el-row :gutter="16" style="margin-bottom: 20px;">
    <el-col :span="6">
      <el-card shadow="hover" body-style="text-align: center; padding: 20px;">
        <el-statistic title="结算人数" :value="store.overview.total_people">
          <template #suffix>人</template>
        </el-statistic>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover" body-style="text-align: center; padding: 20px;">
        <el-statistic
          title="工资总额"
          :value="store.overview.total_salary"
          :precision="2"
          :prefix="'¥'"
        />
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover" body-style="text-align: center; padding: 20px;">
        <el-statistic title="总出勤工日" :value="store.overview.total_workdays">
          <template #suffix>工日</template>
        </el-statistic>
      </el-card>
    </el-col>
    <el-col :span="6">
      <el-card shadow="hover" body-style="text-align: center; padding: 20px;">
        <el-statistic title="总加班工时" :value="store.overview.total_overtime" :precision="1">
          <template #suffix>小时</template>
        </el-statistic>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
</script>
