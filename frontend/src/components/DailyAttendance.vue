<template>
  <div class="table-card">
    <h3 class="section-title">每日考勤明细</h3>

    <el-tabs v-model="activeTab" class="attendance-tabs">
      <el-tab-pane name="all">
        <template #label>
          <span>全部 <el-badge :value="allSourceData.length" :max="9999" class="tab-badge" /></span>
        </template>
        <div class="tab-toolbar">
          <el-input
            v-model="searchName"
            placeholder="搜索员工姓名"
            clearable
            size="default"
            class="table-search"
          >
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </div>
        <el-table
          :data="pagedAllData"
          stripe
          size="default"
          :max-height="500"
        >
          <el-table-column
            v-for="col in mainColumns"
            :key="col.prop"
            :prop="col.prop"
            :label="col.label"
            :min-width="col.minWidth"
            :sortable="col.sortable || false"
          >
            <template v-if="col.slot === 'wage'" #default="{ row }">
              {{ row[col.prop] != null ? `¥${Number(row[col.prop]).toFixed(2)}` : '-' }}
            </template>
            <template v-else-if="col.slot === 'tag'" #default="{ row }">
              <el-tag v-if="row[col.prop]" :type="row[col.prop].startsWith('异常') ? 'danger' : 'info'" size="small">
                {{ row[col.prop] }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-bar">
          <el-pagination
            v-model:current-page="allPage"
            v-model:page-size="allPageSize"
            :page-sizes="[20, 50, 100]"
            :total="allSourceData.length"
            layout="total, sizes, prev, pager, next"
            background
            small
          />
        </div>
      </el-tab-pane>

      <el-tab-pane name="abnormal">
        <template #label>
          <span>异常 <el-badge :value="abnormalData.length" type="danger" class="tab-badge" /></span>
        </template>
        <div class="tab-toolbar">
          <span class="tab-count">共 {{ abnormalData.length }} 条异常记录</span>
        </div>
        <el-table :data="pagedAbnormalData" stripe size="default" :max-height="500">
          <el-table-column prop="日期" label="日期" min-width="55" />
          <el-table-column prop="姓名" label="姓名" min-width="70" />
          <el-table-column prop="工种" label="工种" min-width="70" />
          <el-table-column prop="当日工时" label="工时" min-width="55" />
          <el-table-column prop="当日总工资" label="日工资" min-width="80">
            <template #default="{ row }">
              {{ row.当日总工资 ? `¥${row.当日总工资.toFixed(2)}` : '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="备注" label="备注" min-width="180">
            <template #default="{ row }">
              <el-tag type="danger" size="small" effect="light">{{ row.备注 }}</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination-bar">
          <el-pagination
            v-model:current-page="abnormalPage"
            v-model:page-size="abnormalPageSize"
            :page-sizes="[20, 50, 100]"
            :total="abnormalData.length"
            layout="total, sizes, prev, pager, next"
            background
            small
          />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAttendanceStore } from '@/stores/attendance'

const store = useAttendanceStore()
const activeTab = ref('all')
const searchName = ref('')

// Pagination state per tab
const allPage = ref(1)
const allPageSize = ref(20)
const abnormalPage = ref(1)
const abnormalPageSize = ref(20)

interface ColDef {
  prop: string
  label: string
  minWidth: string
  slot?: string
  sortable?: boolean
}

const mainColumns: ColDef[] = [
  { prop: '日期', label: '日期', minWidth: '55' },
  { prop: '姓名', label: '姓名', minWidth: '70' },
  { prop: '工种', label: '工种', minWidth: '70' },
  { prop: '上班打卡时间', label: '上班', minWidth: '65' },
  { prop: '下班打卡时间', label: '下班', minWidth: '65' },
  { prop: '当日工时', label: '工时', minWidth: '55' },
  { prop: '基本工时', label: '基本', minWidth: '55' },
  { prop: '加班工时', label: '加班', minWidth: '55' },
  { prop: '当日总工资', label: '日工资', minWidth: '80', slot: 'wage' },
  { prop: '备注', label: '备注', minWidth: '120', slot: 'tag' },
]

// All tab: search + pagination
const allSourceData = computed(() => {
  if (!searchName.value) return store.dailyData
  return store.dailyData.filter((r) => r.姓名.includes(searchName.value))
})

const pagedAllData = computed(() => {
  const start = (allPage.value - 1) * allPageSize.value
  return allSourceData.value.slice(start, start + allPageSize.value)
})

// Abnormal tab: pagination
const abnormalData = computed(() =>
  store.dailyData.filter((r) => r.备注 && r.备注 !== ''),
)

const pagedAbnormalData = computed(() => {
  const start = (abnormalPage.value - 1) * abnormalPageSize.value
  return abnormalData.value.slice(start, start + abnormalPageSize.value)
})

// Reset page on search/tab change
watch(searchName, () => { allPage.value = 1 })
watch(activeTab, () => {
  allPage.value = 1
  abnormalPage.value = 1
})
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

.tab-toolbar {
  display: flex;
  align-items: center;
  margin-bottom: var(--space-3);
}
.tab-toolbar .table-search {
  width: 220px;
}
.tab-count {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

.tab-badge {
  margin-left: 4px;
}
.tab-badge :deep(.el-badge__content) {
  font-size: 11px;
  height: 16px;
  line-height: 16px;
  padding: 0 5px;
}

.attendance-tabs :deep(.el-tabs__header) {
  margin-bottom: var(--space-3);
}

.pagination-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: var(--space-4);
}

@media (max-width: 640px) {
  .table-card {
    padding: var(--space-3);
  }
  .tab-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-2);
  }
  .tab-toolbar .table-search {
    width: 100%;
  }
  .pagination-bar {
    justify-content: center;
  }
}
</style>
