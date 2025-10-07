<script setup lang="ts">
import backet from "../../public/backet.png";
import {useRouter} from "vue-router";

const router = useRouter()

const backet_click = () => {
  router.push({ name: 'Backet' })
}
</script>

<template>
  <div class="menu">
    <button class="all">Все</button>
    <button class="exist">В наличии</button>
    <button class="wait">Предзаказ</button>
    <button class="backet" @click="backet_click">
      <img :src="backet" class="backet_icon" alt="bad bar"/>
    </button>
    <div class="money">RUB</div>
  </div>

</template>

<style scoped>
.menu{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

button{
  font-size: 12px;
  padding: 8px 20px;
  border-radius: 22px;
  background-color: var(--white);
  border: 1px solid var(--grey);
}

.all{
  background-color: var(--black);
  color: var(--white);
  border: 1px solid var(--black);
}

.backet_icon{
  width: 16px;
  height: 16px;
}

.backet{
  padding: 6px;
  padding-bottom: 2px;
}

.money{
  display: flex;
  align-items: center;
  color: var(--text_grey);
}
</style>
