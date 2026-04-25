<template>
  <div class="table-card">
    <div class="table-header">
      <div class="table-header-left">
        <h3 class="section-title" style="margin-bottom:0">工资汇总表</h3>
        <el-tag effect="plain" round size="small">{{ filteredData.length }}人</el-tag>
      </div>
      <el-input
        v-model="searchName"
        placeholder="搜索员工姓名"
        clearable
        class="table-search"
        size="default"
      >
        <template #prefix><el-icon><Search /></el-icon></template>
      </el-input>
    </div>

    <el-table
      :data="pagedData"
      stripe
      size="default"
      :default-sort="{ prop: '序号', order: 'ascending' }"
      :row-class-name="rowClassName"
      class="salary-table"
    >
      <el-table-column prop="序号" label="序号" min-width="55" sortable />
      <el-table-column prop="姓名" label="姓名" min-width="75" sortable />
      <el-table-column prop="工种" label="工种" min-width="75" sortable />
      <el-table-column prop="出勤工日" label="出勤工日" min-width="80" sortable />
      <el-table-column prop="日工资" label="日工资" min-width="90" sortable>
        <template #default="{ row }">{{ row.日工资 ? `¥${row.日工资.toFixed(0)}` : '-' }}</template>
      </el-table-column>
      <el-table-column prop="加班工时" label="加班工时" min-width="80" sortable />
      <el-table-column prop="加班工资" label="加班工资" min-width="90" sortable>
        <template #default="{ row }">{{ row.加班工资 ? `¥${row.加班工资.toFixed(0)}` : '-' }}</template>
      </el-table-column>
      <el-table-column prop="工资总额" label="工资总额" min-width="110" sortable>
        <template #default="{ row }">
          <strong class="salary-total">¥{{ row.工资总额.toFixed(2) }}</strong>
        </template>
      </el-table-column>
      <el-table-column prop="备注" label="备注" min-width="140">
        <template #default="{ row }">
          <el-tag v-if="row.备注" type="warning" size="small" effect="light">{{ row.备注 }}</el-tag>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination-bar">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[20, 50, 100]"
        :total="filteredData.length"
        layout="total, sizes, prev, pager, next"
        background
        small
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const searchName = ref('')
const currentPage = ref(1)
const pageSize = ref(20)

const filteredData = computed(() => {
  if (!searchName.value) return store.salaryData
  return store.salaryData.filter((r) => r.姓名.includes(searchName.value))
})

const pagedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

// Reset to page 1 when search changes
watch(searchName, () => { currentPage.value = 1 })

function rowClassName({ row }: { row: any }) {
  return row.备注 && row.备注 !== '' ? 'warning-row' : ''
}
</script>

<style scoped>
.table-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: var(--space-5);
  box-shadow: var(--shadow-xs);
  border: 1px solid var(--color-border-light);
  margin-bottom: var(--space-5);
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-4);
}
.table-header-left {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.table-search {
  width: 220px;
}

.salary-total {
  color: var(--color-brand);
}

.salary-table .warning-row {
  --el-table-tr-bg-color: var(--color-warning-light);
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-4);
}
</style>
