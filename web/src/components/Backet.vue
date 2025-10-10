<script setup lang="ts">
import {store} from "../store.js";
import {products} from "../types/Data.ts";
import {useRouter} from "vue-router";
import trash from "../../public/trash.svg";

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

const open_delivery_click = () => {
  router.push({ name: 'Delivery' })
}

// Получить все товары в корзине
const getBacketItems = () => {
  const items = []

  // Рубашка
  products[1].sizes?.forEach((size, index) => {
    if (store.rubaska_count[index] > 0) {
      items.push({
        product: products[1],
        variant: size,
        count: store.rubaska_count[index],
        productIndex: 1,
        variantIndex: index
      })
    }
  })

  // Дождевик
  products[2].sizes?.forEach((size, index) => {
    if (store.rain_count[index] > 0) {
      items.push({
        product: products[2],
        variant: size,
        count: store.rain_count[index],
        productIndex: 2,
        variantIndex: index
      })
    }
  })

  // Фляга
  products[0].types?.forEach((type, index) => {
    if (store.flyaga_count[index] > 0) {
      items.push({
        product: products[0],
        variant: type,
        count: store.flyaga_count[index],
        productIndex: 0,
        variantIndex: index
      })
    }
  })

  return items
}

// Изменить количество товара
const changeCount = (productIndex: number, variantIndex: number, delta: number) => {
  if (productIndex === 1) {
    store.rubaska_count[variantIndex] = Math.max(0, store.rubaska_count[variantIndex] + delta)
  } else if (productIndex === 2) {
    store.rain_count[variantIndex] = Math.max(0, store.rain_count[variantIndex] + delta)
  } else if (productIndex === 0) {
    store.flyaga_count[variantIndex] = Math.max(0, store.flyaga_count[variantIndex] + delta)
  }
}

// Удалить товар
const removeItem = (productIndex: number, variantIndex: number) => {
  if (productIndex === 1) {
    store.rubaska_count[variantIndex] = 0
  } else if (productIndex === 2) {
    store.rain_count[variantIndex] = 0
  } else if (productIndex === 0) {
    store.flyaga_count[variantIndex] = 0
  }
}

// Подсчет итоговой суммы
const getTotalPrice = () => {
  const items = getBacketItems()
  return items.reduce((sum, item) => {
    const price = store.money_type === 'RUB' ? item.product.priceRUB : item.product.priceEUR
    return sum + price * item.count
  }, 0)
}

const formatPrice = (price: number) => {
  return price.toLocaleString('ru-RU')
}

const getCurrency = () => {
  return store.money_type === 'RUB' ? '₽' : '€'
}

const getDeliveryDescription = () => {
  switch(store.selected_delivery_id) {
    case 'camp':
      return 'Бесплатно'
    default:
      return 'Сколько-то денег, рассчитаем позже и напишем цену'
  }
}
</script>

<template>
  <div class="backet">
    <div class="header">
      <div class="back" @click="back_click">←</div>
      <div class="title">Корзина</div>
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

    <div class="items">
      <div class="item"
           v-for="(item, index) in getBacketItems()"
           :key="index"
      >
        <img :src="item.product.image" class="item_image" alt="">
        <div class="item_info">
          <div class="item_name">{{item.product.name}}</div>
          <div class="item_variant">{{item.variant}}</div>
          <div class="item_price">
            {{formatPrice(store.money_type === 'RUB' ? item.product.priceRUB : item.product.priceEUR)}}{{getCurrency()}}
          </div>
        </div>
        <button class="delete_btn" @click="removeItem(item.productIndex, item.variantIndex)">
          <img :src="trash" alt="delete" class="trash_icon">
        </button>
        <div class="item_controls">
          <button class="control_btn" @click="changeCount(item.productIndex, item.variantIndex, -1)">−</button>
          <div class="item_count">{{item.count.toString().padStart(2, '0')}}</div>
          <button class="control_btn" @click="changeCount(item.productIndex, item.variantIndex, 1)">+</button>
        </div>
      </div>
    </div>

    <div class="delivery" @click="open_delivery_click">
      <div class="delivery_label">Доставка: {{store.delivery_type}}</div>
      <div class="delivery_desc">{{getDeliveryDescription()}}</div>
      <div class="delivery_arrow">›</div>
    </div>

    <div class="summary">
      <div class="summary_row">
        <span>Товары:</span>
        <span>{{formatPrice(getTotalPrice())}}{{getCurrency()}}</span>
      </div>
      <div class="summary_row">
        <span>Доставка:</span>
        <span v-if="store.selected_delivery_id === 'camp'">0{{getCurrency()}}</span>
        <span v-else>?{{getCurrency()}}</span>
      </div>
      <div class="summary_row total">
        <span>Итого:</span>
        <span v-if="store.selected_delivery_id === 'camp'">{{formatPrice(getTotalPrice())}}{{getCurrency()}}</span>
        <span v-else>?{{getCurrency()}}</span>
      </div>
    </div>

    <button class="donate_btn">
      Хочу задонатить Бару!
    </button>

    <button class="pay_btn">
      К оплате
    </button>
  </div>
</template>

<style scoped>
.backet {
  padding: 20px;
  padding-bottom: 100px;
}

.header {
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  margin-bottom: 20px;
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

.items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  position: relative;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--grey);
}

.item_image {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid var(--grey);
}

.item_info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.item_name {
  font-weight: bold;
  font-size: 14px;
}

.item_variant {
  font-size: 12px;
  color: var(--text_grey);
}

.item_price {
  font-size: 14px;
  color: var(--red);
  font-weight: bold;
  font-family: PT Mono, sans-serif;
}

.delete_btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  position: absolute;
  top: 0;
  right: 0;
}

.trash_icon {
  width: 20px;
  height: 20px;
}

.item_controls {
  display: flex;
  align-items: center;
  gap: 8px;
  position: absolute;
  bottom: 16px;
  right: 0;
}

.control_btn {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid var(--black);
  background-color: var(--white);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 18px;
  line-height: 1;
}

.item_count {
  font-size: 14px;
  font-weight: bold;
  min-width: 24px;
  text-align: center;
}

.delivery {
  margin-top: 20px;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid var(--grey);
  cursor: pointer;
  position: relative;
}

.delivery_label {
  font-weight: bold;
  font-size: 14px;
  margin-bottom: 4px;
}

.delivery_desc {
  font-size: 12px;
  color: var(--text_grey);
  line-height: 1.4;
}

.delivery_arrow {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  right: 16px;
  font-size: 24px;
  color: var(--text_grey);
}

.summary {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.summary_row {
  display: flex;
  justify-content: space-between;
  font-size: 16px;
}

.summary_row.total {
  font-weight: bold;
  font-size: 18px;
  margin-top: 8px;
}

.donate_btn {
  width: 100%;
  margin-top: 16px;
  padding: 12px;
  border-radius: 22px;
  border: none;
  background-color: var(--white);
  color: var(--red);
  font-size: 14px;
  font-weight: bold;
  cursor: pointer;
  border: 2px solid var(--red);
}

.pay_btn {
  width: 100%;
  margin-top: 12px;
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
