<template>
  <el-card shadow="hover" style="margin-bottom: 20px;">
    <template #header>
      <div style="display: flex; align-items: center; justify-content: space-between;">
        <strong>工资汇总表</strong>
        <el-input
          v-model="searchName"
          placeholder="搜索员工姓名"
          clearable
          style="width: 200px;"
          size="small"
        >
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
      </div>
    </template>

    <el-table
      :data="filteredData"
      stripe
      border
      size="small"
      :default-sort="{ prop: '序号', order: 'ascending' }"
      style="width: 100%;"
      :row-class-name="rowClassName"
    >
      <el-table-column prop="序号" label="序号" width="60" sortable />
      <el-table-column prop="姓名" label="姓名" width="80" sortable />
      <el-table-column prop="工种" label="工种" width="80" sortable />
      <el-table-column prop="出勤工日" label="出勤工日" width="80" sortable />
      <el-table-column prop="日工资" label="日工资" width="100" sortable>
        <template #default="{ row }">{{ row.日工资 ? `¥${row.日工资.toFixed(0)}` : '-' }}</template>
      </el-table-column>
      <el-table-column prop="加班工时" label="加班工时" width="80" sortable />
      <el-table-column prop="加班工资" label="加班工资" width="100" sortable>
        <template #default="{ row }">{{ row.加班工资 ? `¥${row.加班工资.toFixed(0)}` : '-' }}</template>
      </el-table-column>
      <el-table-column prop="工资总额" label="工资总额" width="120" sortable>
        <template #default="{ row }">
          <strong>¥{{ row.工资总额.toFixed(2) }}</strong>
        </template>
      </el-table-column>
      <el-table-column prop="备注" label="备注" min-width="150">
        <template #default="{ row }">
          <el-tag v-if="row.备注" type="warning" size="small">{{ row.备注 }}</el-tag>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const searchName = ref('')

const filteredData = computed(() => {
  if (!searchName.value) return store.salaryData
  return store.salaryData.filter((r) => r.姓名.includes(searchName.value))
})

function rowClassName({ row }: { row: any }) {
  return row.备注 && row.备注 !== '' ? 'warning-row' : ''
}
</script>

<style>
.el-table .warning-row {
  --el-table-tr-bg-color: var(--el-color-warning-light-9);
}
</style>
