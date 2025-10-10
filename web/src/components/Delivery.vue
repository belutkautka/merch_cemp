<script setup lang="ts">
import {store} from "../store.js";
import {useRouter} from "vue-router";

const router = useRouter()

const back_click = () => {
  router.back()
}

const open_money_types_click = () => {
  store.money_open = !store.money_open
}

const change_money_type = (value: string) => {
  store.money_type = value
  store.money_open = false
}

const deliveryMethods = [
  {
    id: 'camp',
    name: 'Кэмп',
    description: 'Бесплатно',
    price: 0
  },
  {
    id: 'pvz',
    name: 'Ближайший ПВЗ',
    description: 'Сколько-то денег, рассчитаем позже и напишем цену',
    price: null
  },
  {
    id: 'courier_ekb',
    name: 'Курьером по Екатеринбургу',
    description: 'Сколько-то денег, рассчитаем позже и напишем цену',
    price: null
  },
  {
    id: 'worldwide',
    name: 'Worldwide',
    description: 'Сколько-то денег, рассчитаем позже и напишем цену',
    price: null
  },
  {
    id: 'other',
    name: 'Другое',
    description: null,
    price: null
  }
]

const selectDelivery = (methodId: string) => {
  const method = deliveryMethods.find(m => m.id === methodId)
  if (method) {
    store.delivery_type = method.name
    store.selected_delivery_id = methodId
    if (method.price !== null) {
      store.delivery_price = method.price
    }
  }
}

const continueClick = () => {
  router.back()
}
</script>

<template>
  <div class="delivery_page">
    <div class="header">
      <div class="back" @click="back_click">←</div>
      <div class="title">Доставка</div>
      <div class="money_type" @click="open_money_types_click">{{store.money_type}} ᨆ</div>
      <div class="other_money"
           @click="change_money_type('RUB')"
           v-if="(store.money_type != 'RUB') && (store.money_open)"
      >RUB</div>
      <div class="other_money"
           @click="change_money_type('EUR')"
           v-if="(store.money_type != 'EUR') && (store.money_open)"
      >EUR</div>
    </div>

    <div class="methods">
      <div
        class="method"
        v-for="method in deliveryMethods"
        :key="method.id"
        @click="selectDelivery(method.id)"
      >
        <div class="radio">
          <div class="radio_outer">
            <div class="radio_inner" v-if="store.selected_delivery_id === method.id"></div>
          </div>
        </div>
        <div class="method_info">
          <div class="method_name">{{method.name}}</div>
          <div class="method_desc" v-if="method.description">{{method.description}}</div>
        </div>
      </div>
    </div>

    <button class="continue_btn" @click="continueClick">
      Продолжить
    </button>
  </div>
</template>

<style scoped>
.delivery_page {
  padding: 20px;
  padding-bottom: 100px;
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 30px;
}

.back {
  color: var(--black);
  position: absolute;
  left: 0;
  font-size: 24px;
  cursor: pointer;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.money_type {
  color: var(--black);
  position: absolute;
  right: 0;
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 22px;
  border: 1px solid var(--grey);
  background-color: var(--white);
  cursor: pointer;
}

.other_money {
  position: absolute;
  top: 40px;
  right: 0;
  z-index: 1;
  background-color: var(--grey);
  padding: 8px 0;
  width: 66px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  justify-content: center;
  cursor: pointer;
}

.methods {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.method {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 20px 0;
  border-bottom: 1px solid var(--grey);
  cursor: pointer;
}

.method:first-child {
  padding-top: 0;
}

.radio {
  padding-top: 2px;
}

.radio_outer {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--black);
  display: flex;
  align-items: center;
  justify-content: center;
  box-sizing: border-box;
}

.radio_inner {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background-color: var(--red);
}

.method_info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.method_name {
  font-weight: bold;
  font-size: 16px;
}

.method_desc {
  font-size: 12px;
  color: var(--text_grey);
  line-height: 1.4;
}

.continue_btn {
  width: 100%;
  padding: 14px;
  border-radius: 22px;
  border: none;
  background-color: var(--black);
  color: var(--white);
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  max-width: 460px;
  width: calc(100% - 40px);
}
</style>
