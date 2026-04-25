<template>
  <el-card shadow="hover" style="margin-bottom: 20px;">
    <template #header><strong>每日考勤明细</strong></template>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="全部记录" name="all">
        <el-table :data="store.dailyData" stripe border size="small" :max-height="500">
          <el-table-column prop="日期" label="日期" width="60" />
          <el-table-column prop="姓名" label="姓名" width="80" />
          <el-table-column prop="工种" label="工种" width="80" />
          <el-table-column prop="上班打卡时间" label="上班" width="70" />
          <el-table-column prop="下班打卡时间" label="下班" width="70" />
          <el-table-column prop="当日工时" label="工时" width="60" />
          <el-table-column prop="基本工时" label="基本" width="60" />
          <el-table-column prop="加班工时" label="加班" width="60" />
          <el-table-column prop="当日总工资" label="日工资" width="90">
            <template #default="{ row }">
              {{ row.当日总工资 ? `¥${row.当日总工资.toFixed(2)}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="备注" label="备注" min-width="120">
            <template #default="{ row }">
              <el-tag v-if="row.备注" :type="row.备注.startsWith('异常') ? 'danger' : 'info'" size="small">
                {{ row.备注 }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="搜索员工" name="search">
        <el-input
          v-model="searchName"
          placeholder="搜索员工姓名"
          clearable
          style="width: 200px; margin-bottom: 12px;"
          size="small"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-table :data="filteredDaily" stripe border size="small" :max-height="500">
          <el-table-column prop="日期" label="日期" width="60" />
          <el-table-column prop="姓名" label="姓名" width="80" />
          <el-table-column prop="工种" label="工种" width="80" />
          <el-table-column prop="上班打卡时间" label="上班" width="70" />
          <el-table-column prop="下班打卡时间" label="下班" width="70" />
          <el-table-column prop="当日工时" label="工时" width="60" />
          <el-table-column prop="基本工时" label="基本" width="60" />
          <el-table-column prop="加班工时" label="加班" width="60" />
          <el-table-column prop="当日总工资" label="日工资" width="90">
            <template #default="{ row }">
              {{ row.当日总工资 ? `¥${row.当日总工资.toFixed(2)}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="备注" label="备注" min-width="120" />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="异常记录" name="abnormal">
        <p style="color: #909399; margin-bottom: 8px;">共 {{ abnormalData.length }} 条异常记录</p>
        <el-table :data="abnormalData" stripe border size="small" :max-height="500">
          <el-table-column prop="日期" label="日期" width="60" />
          <el-table-column prop="姓名" label="姓名" width="80" />
          <el-table-column prop="工种" label="工种" width="80" />
          <el-table-column prop="当日工时" label="工时" width="60" />
          <el-table-column prop="当日总工资" label="日工资" width="90">
            <template #default="{ row }">
              {{ row.当日总工资 ? `¥${row.当日总工资.toFixed(2)}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="备注" label="备注" min-width="200">
            <template #default="{ row }">
              <el-tag type="danger" size="small">{{ row.备注 }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const activeTab = ref('all')
const searchName = ref('')

const filteredDaily = computed(() => {
  if (!searchName.value) return []
  return store.dailyData.filter((r) => r.姓名.includes(searchName.value))
})

const abnormalData = computed(() =>
  store.dailyData.filter((r) => r.备注 && r.备注 !== ''),
)
</script>
