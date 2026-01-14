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

const recipientOptions = [
  { id: 'me', name: 'Я' },
  { id: 'gift', name: 'Это подарок' }
]

const deliveryMethods = [
  {
    id: 'pvz',
    name: 'Ближайший ПВЗ',
    description: 'Пришлите ссылку на удобный ПВЗ (Яндекс/2ГИС/сайт службы). Стоимость доставки рассчитаем и согласуем перед отправкой.',
    price: null
  },
  {
    id: 'courier_ekb',
    name: 'Курьером по Екатеринбургу',
    description: 'Доставим курьером. Укажите адрес — время и стоимость согласуем в переписке перед отправкой.',
    price: null
  },
  {
    id: 'worldwide',
    name: 'Worldwide',
    description: 'Международная доставка. Укажите страну и адрес — стоимость и сроки рассчитаем и подтвердим перед отправкой.',
    price: null
  },
  {
    id: 'other',
    name: 'Другое',
    description: null,
    price: null
  }
]

const selectRecipient = (recipientId: string) => {
  store.recipient_type = recipientId
}

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

    <!-- Recipient selection -->
    <div class="section">
      <div class="section_title">Получатель</div>
      <div class="recipient_options">
        <div
          class="recipient_option"
          v-for="option in recipientOptions"
          :key="option.id"
          :class="{ active: store.recipient_type === option.id }"
          @click="selectRecipient(option.id)"
        >
          {{ option.name }}
        </div>
      </div>
    </div>

    <!-- Delivery methods -->
    <div class="section">
      <div class="section_title">Способ доставки</div>
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
    </div>

    <!-- PVZ fields -->
    <div class="form_section" v-if="store.selected_delivery_id === 'pvz'">
      <div class="section_title">Данные для доставки в ПВЗ</div>
      <div class="form_field">
        <label>Город</label>
        <input type="text" v-model="store.pvz_city" placeholder="Введите город" />
      </div>
      <div class="form_field">
        <label>Ссылка на ПВЗ (или адрес текстом)</label>
        <input type="text" v-model="store.pvz_link" placeholder="Ссылка или адрес ПВЗ" />
      </div>
      <div class="form_field">
        <label>ФИО получателя</label>
        <input type="text" v-model="store.pvz_recipient_name" placeholder="Иванов Иван Иванович" />
      </div>
      <div class="form_field">
        <label>Телефон получателя</label>
        <input type="tel" v-model="store.pvz_recipient_phone" placeholder="+7 999 123 45 67" />
      </div>
    </div>

    <!-- Courier EKB fields -->
    <div class="form_section" v-if="store.selected_delivery_id === 'courier_ekb'">
      <div class="section_title">Данные для курьерской доставки</div>
      <div class="form_field">
        <label>ФИО получателя</label>
        <input type="text" v-model="store.courier_recipient_name" placeholder="Иванов Иван Иванович" />
      </div>
      <div class="form_field">
        <label>Адрес (улица/дом/кв)</label>
        <input type="text" v-model="store.courier_address" placeholder="ул. Ленина, д. 1, кв. 1" />
      </div>
      <div class="form_field">
        <label>Комментарий (подъезд/этаж/домофон/удобное время)</label>
        <input type="text" v-model="store.courier_comment" placeholder="Подъезд 1, этаж 5, домофон 123" />
      </div>
    </div>

    <!-- Worldwide fields -->
    <div class="form_section" v-if="store.selected_delivery_id === 'worldwide'">
      <div class="section_title">Данные для международной доставки</div>
      <div class="form_field">
        <label>ФИО получателя</label>
        <input type="text" v-model="store.worldwide_recipient_name" placeholder="Иванов Иван Иванович" />
      </div>
      <div class="form_field">
        <label>Страна</label>
        <input type="text" v-model="store.worldwide_country" placeholder="Введите страну" />
      </div>
      <div class="form_field">
        <label>Город</label>
        <input type="text" v-model="store.worldwide_city" placeholder="Введите город" />
      </div>
      <div class="form_field">
        <label>Индекс</label>
        <input type="text" v-model="store.worldwide_zip" placeholder="Почтовый индекс" />
      </div>
      <div class="form_field">
        <label>Адрес</label>
        <input type="text" v-model="store.worldwide_address" placeholder="Улица, дом, квартира" />
      </div>
      <div class="form_field">
        <label>Телефон получателя</label>
        <input type="tel" v-model="store.worldwide_phone" placeholder="+1 234 567 8900" />
      </div>
      <div class="form_field">
        <label>Комментарий (опционально)</label>
        <input type="text" v-model="store.worldwide_comment" placeholder="Дополнительная информация" />
      </div>
    </div>

    <!-- Other fields -->
    <div class="form_section" v-if="store.selected_delivery_id === 'other'">
      <div class="section_title">Опишите желаемый способ доставки</div>
      <div class="form_field">
        <label>Комментарий</label>
        <textarea v-model="store.other_comment" placeholder="Опишите, как вы хотите получить заказ"></textarea>
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

.section {
  margin-bottom: 24px;
}

.section_title {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 12px;
  color: var(--text_grey);
}

.recipient_options {
  display: flex;
  gap: 12px;
}

.recipient_option {
  flex: 1;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--grey);
  text-align: center;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s ease;
}

.recipient_option.active {
  border-color: var(--black);
  background-color: var(--black);
  color: var(--white);
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

.form_section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--grey);
}

.form_field {
  margin-bottom: 16px;
}

.form_field label {
  display: block;
  font-size: 12px;
  color: var(--text_grey);
  margin-bottom: 6px;
}

.form_field input {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--grey);
  font-size: 14px;
  box-sizing: border-box;
  background-color: var(--white);
}

.form_field input:focus {
  outline: none;
  border-color: var(--black);
}

.form_field input::placeholder {
  color: var(--text_grey);
  opacity: 0.6;
}

.form_field textarea {
  width: 100%;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--grey);
  font-size: 14px;
  box-sizing: border-box;
  background-color: var(--white);
  min-height: 100px;
  resize: vertical;
  font-family: inherit;
}

.form_field textarea:focus {
  outline: none;
  border-color: var(--black);
}

.form_field textarea::placeholder {
  color: var(--text_grey);
  opacity: 0.6;
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
