<script setup lang="ts">
import {store} from "../store.js";
import {products} from "../types/Data.ts";
import {useRouter} from "vue-router";
import trash from "../../public/trash.svg";
import type Product from "../types/Product.ts";

// Поиск товара по ID вместо индекса массива
const getProductById = (id: number): Product | undefined => {
  return products.find(p => p.id === id)
}

interface BacketItem {
  product: Product;
  variant: string;
  count: number;
  productIndex: number;
  variantIndex: number;
}

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
const getBacketItems = (): BacketItem[] => {
  const items: BacketItem[] = []

  // Фляга (id: 0)
  const flyaga = getProductById(0)
  flyaga?.types?.forEach((type, index) => {
    if (store.flyaga_count[index]! > 0) {
      items.push({
        product: flyaga,
        variant: type,
        count: store.flyaga_count[index]!,
        productIndex: 0,
        variantIndex: index
      })
    }
  })

  // Рубашка (id: 1)
  const rubashka = getProductById(1)
  rubashka?.sizes?.forEach((size, index) => {
    if (store.rubaska_count[index]! > 0) {
      items.push({
        product: rubashka,
        variant: size,
        count: store.rubaska_count[index]!,
        productIndex: 1,
        variantIndex: index
      })
    }
  })

  // Дождевик M/L (id: 2)
  const rainML = getProductById(2)
  rainML?.sizes?.forEach((size, index) => {
    if (store.rain_ML_count[index]! > 0) {
      items.push({
        product: rainML,
        variant: size,
        count: store.rain_ML_count[index]!,
        productIndex: 2,
        variantIndex: index
      })
    }
  })

  // Дождевик XL/XXL (id: 3)
  const rainXLXXL = getProductById(3)
  rainXLXXL?.sizes?.forEach((size, index) => {
    if (store.rain_XLXXL_count[index]! > 0) {
      items.push({
        product: rainXLXXL,
        variant: size,
        count: store.rain_XLXXL_count[index]!,
        productIndex: 3,
        variantIndex: index
      })
    }
  })

  return items
}

// Изменить количество товара
const changeCount = (productIndex: number, variantIndex: number, delta: number) => {
  if (productIndex === 0) {
    store.flyaga_count[variantIndex] = Math.max(0, store.flyaga_count[variantIndex]! + delta)
  } else if (productIndex === 1) {
    store.rubaska_count[variantIndex] = Math.max(0, store.rubaska_count[variantIndex]! + delta)
  } else if (productIndex === 2) {
    store.rain_ML_count[variantIndex] = Math.max(0, store.rain_ML_count[variantIndex]! + delta)
  } else if (productIndex === 3) {
    store.rain_XLXXL_count[variantIndex] = Math.max(0, store.rain_XLXXL_count[variantIndex]! + delta)
  }
}

// Удалить товар
const removeItem = (productIndex: number, variantIndex: number) => {
  if (productIndex === 0) {
    store.flyaga_count[variantIndex] = 0
  } else if (productIndex === 1) {
    store.rubaska_count[variantIndex] = 0
  } else if (productIndex === 2) {
    store.rain_ML_count[variantIndex] = 0
  } else if (productIndex === 3) {
    store.rain_XLXXL_count[variantIndex] = 0
  }
}

// Подсчет итоговой суммы
const getTotalPrice = (): number => {
  const items = getBacketItems()
  return items.reduce((sum, item) => {
    const price = store.money_type === 'RUB' ? item.product!.priceRUB : item.product!.priceEUR
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
  return 'Стоимость рассчитаем и согласуем перед отправкой'
}

// Стоимость подарочной упаковки
const GIFT_PACKAGING_PRICE_RUB = 300
const GIFT_PACKAGING_PRICE_EUR = 3

const getGiftPackagingPrice = (): number => {
  if (store.recipient_type !== 'gift') return 0
  return store.money_type === 'RUB' ? GIFT_PACKAGING_PRICE_RUB : GIFT_PACKAGING_PRICE_EUR
}

const getFinalPrice = (): number => {
  return getTotalPrice() + getGiftPackagingPrice()
}

// Проверка заполнения обязательных полей доставки
const isDeliveryValid = (): boolean => {
  if (store.selected_delivery_id === 'pvz') {
    return !!(store.pvz_city && store.pvz_link && store.pvz_recipient_name && store.pvz_recipient_phone)
  } else if (store.selected_delivery_id === 'courier_ekb') {
    return !!(store.courier_address && store.courier_recipient_name)
  } else if (store.selected_delivery_id === 'worldwide') {
    return !!(store.worldwide_country && store.worldwide_city && store.worldwide_zip && store.worldwide_address && store.worldwide_phone && store.worldwide_recipient_name)
  } else if (store.selected_delivery_id === 'other') {
    return !!store.other_comment
  }
  return true
}

const getDeliveryError = (): string => {
  if (store.selected_delivery_id === 'pvz') {
    if (!store.pvz_city || !store.pvz_link || !store.pvz_recipient_name || !store.pvz_recipient_phone) {
      return 'Заполните данные для доставки в ПВЗ'
    }
  } else if (store.selected_delivery_id === 'courier_ekb') {
    if (!store.courier_address || !store.courier_recipient_name) {
      return 'Укажите ФИО и адрес для курьерской доставки'
    }
  } else if (store.selected_delivery_id === 'worldwide') {
    if (!store.worldwide_country || !store.worldwide_city || !store.worldwide_zip || !store.worldwide_address || !store.worldwide_phone || !store.worldwide_recipient_name) {
      return 'Заполните данные для международной доставки'
    }
  } else if (store.selected_delivery_id === 'other') {
    if (!store.other_comment) {
      return 'Опишите желаемый способ доставки'
    }
  }
  return ''
}

// Отправка заказа в Telegram бота
const handlePayClick = () => {
  // Собираем данные о доставке в зависимости от выбранного способа
  let delivery_details = {}

  if (store.selected_delivery_id === 'pvz') {
    delivery_details = {
      city: store.pvz_city,
      pvz_link: store.pvz_link,
      recipient_name: store.pvz_recipient_name,
      recipient_phone: store.pvz_recipient_phone,
    }
  } else if (store.selected_delivery_id === 'courier_ekb') {
    delivery_details = {
      recipient_name: store.courier_recipient_name,
      address: store.courier_address,
      comment: store.courier_comment,
    }
  } else if (store.selected_delivery_id === 'worldwide') {
    delivery_details = {
      recipient_name: store.worldwide_recipient_name,
      country: store.worldwide_country,
      city: store.worldwide_city,
      zip: store.worldwide_zip,
      address: store.worldwide_address,
      phone: store.worldwide_phone,
      comment: store.worldwide_comment,
    }
  } else if (store.selected_delivery_id === 'other') {
    delivery_details = {
      comment: store.other_comment,
    }
  }

  const data = {
    order: {
      // Фляга - 3 типа
      flyaga_bad_bar: store.flyaga_count[0] || 0,
      flyaga_horse: store.flyaga_count[1] || 0,
      flyaga_rectal: store.flyaga_count[2] || 0,

      // Рубашка - 9 размеров (42-58)
      rubashka_42: store.rubaska_count[0] || 0,
      rubashka_44: store.rubaska_count[1] || 0,
      rubashka_46: store.rubaska_count[2] || 0,
      rubashka_48: store.rubaska_count[3] || 0,
      rubashka_50: store.rubaska_count[4] || 0,
      rubashka_52: store.rubaska_count[5] || 0,
      rubashka_54: store.rubaska_count[6] || 0,
      rubashka_56: store.rubaska_count[7] || 0,
      rubashka_58: store.rubaska_count[8] || 0,

      // Дождевик M/L
      rain_M_L: store.rain_ML_count[0] || 0,

      // Дождевик XL/XXL
      rain_XL_XXL: store.rain_XLXXL_count[0] || 0,
    },
    rubashka_height: store.selected_height,
    recipient: store.recipient_type === 'gift' ? 'Это подарок' : 'Я',
    gift_packaging: store.recipient_type === 'gift',
    gift_packaging_price: getGiftPackagingPrice(),
    delivery: store.delivery_type,
    delivery_id: store.selected_delivery_id,
    delivery_details: delivery_details,
    currency: store.money_type,
    total_price: getFinalPrice(),
  }

  window.Telegram.WebApp.sendData(JSON.stringify(data))
  window.Telegram.WebApp.close()
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
      <div class="summary_row" v-if="store.recipient_type === 'gift'">
        <span>Подарочная упаковка:</span>
        <span>{{formatPrice(getGiftPackagingPrice())}}{{getCurrency()}}</span>
      </div>
      <div class="summary_row">
        <span>Доставка:</span>
        <span>рассчитаем отдельно</span>
      </div>
      <div class="summary_row total">
        <span>Итого:</span>
        <span>{{formatPrice(getFinalPrice())}}{{getCurrency()}} + доставка</span>
      </div>
    </div>

    <div class="delivery_error" v-if="getDeliveryError()">
      {{ getDeliveryError() }}
    </div>

    <button
      class="pay_btn"
      :class="{ disabled: !isDeliveryValid() }"
      @click="isDeliveryValid() && handlePayClick()"
    >
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

.delivery_error {
  margin-top: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  background-color: #fee2e2;
  color: #dc2626;
  font-size: 14px;
  text-align: center;
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

.pay_btn.disabled {
  background-color: var(--grey);
  cursor: not-allowed;
  opacity: 0.6;
}
</style>
