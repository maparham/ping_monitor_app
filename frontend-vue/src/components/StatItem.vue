<template>
  <div class="stat-item">
    <div class="stat-header">
      <div class="stat-label">{{ label }}</div>
      <div v-if="tooltip" class="tooltip-container">
        <span class="tooltip-icon">ⓘ</span>
        <div class="tooltip-text">{{ tooltip }}</div>
      </div>
    </div>
    <div class="stat-value">
      {{ formatValue(value) }}<span class="stat-unit">{{ unit }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  label: string;
  value: number | null;
  unit: string;
  tooltip?: string;
}

defineProps<Props>();

const formatValue = (val: number | null): string => {
  if (val === undefined || val === null) return 'N/A';
  if (val === Infinity) return '∞';
  return `${val.toFixed(1)}`;
};
</script>

<style scoped>
.stat-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.stat-label {
  font-weight: 600;
  color: #333;
  font-size: 0.9rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
  color: #2c3e50;
}

.stat-unit {
  font-size: 0.8rem;
  color: #666;
  margin-left: 0.25rem;
}

.tooltip-container {
  position: relative;
  display: inline-block;
}

.tooltip-icon {
  color: #666;
  cursor: help;
  font-size: 0.8rem;
}

.tooltip-text {
  visibility: hidden;
  width: 200px;
  background-color: #333;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 8px;
  position: absolute;
  z-index: 1;
  bottom: 125%;
  left: 50%;
  margin-left: -100px;
  font-size: 0.8rem;
  line-height: 1.4;
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
}

.tooltip-text::after {
  content: "";
  position: absolute;
  top: 100%;
  left: 50%;
  margin-left: -5px;
  border-width: 5px;
  border-style: solid;
  border-color: #333 transparent transparent transparent;
}
</style> 