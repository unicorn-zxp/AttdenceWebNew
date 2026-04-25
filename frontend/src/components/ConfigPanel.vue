<template>
  <div style="margin-top: 20px; border-top: 1px solid #e4e7ed; padding-top: 16px;">
    <h3 style="margin: 0 0 12px 0; font-size: 15px;">
      <el-icon><Setting /></el-icon> 计算配置
    </h3>

    <div style="padding: 0 10px;">
      <span style="font-size: 13px; color: #606266;">晚班弹性补齐容差</span>
      <el-slider
        v-model="tolerance"
        :min="1"
        :max="15"
        :step="1"
        :show-tooltip="true"
        :format-tooltip="(val: number) => val + ' 分钟'"
        :disabled="store.calculated"
        @change="store.updateConfig"
      />
      <div style="font-size: 12px; color: #909399; line-height: 1.8;">
        <p>早班进位: &le; 07:40 按 07:30 计</p>
        <p>晚班补齐: &le; {{ tolerance }}分钟 补齐至整点/半点</p>
        <p>工时取整: 按半小时向下取整</p>
        <p>加班分界: 16:30 后算加班</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const tolerance = ref(store.lateTolerance)
</script>
