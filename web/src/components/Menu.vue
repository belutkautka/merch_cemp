<script setup lang="ts">
import backet from "../../public/backet.png";
import {useRouter} from "vue-router";
import {products} from "../types/Data.ts"
import {store} from "../store.js";

const router = useRouter()

const backet_click = () => {
  router.push({ name: 'Backet' })
}

const details_click = (id: number) => {
  store.current_product = id
  store.index = 0
  store.index_size = 0
  store.money_open = false
  router.push({ name: 'ShopItem' })
}

const set_filter_click = (value: boolean|null) => {
  store.filter = value
}

const open_money_types_click = () => {
  store.money_open = !store.money_open
}

const change_money_type = (value: string) => {
  store.money_type = value
  store.money_open = false
}
</script>

<template>
  <div class="menu">
    <button class="menu_button"
            :class="{ selected: store.filter == null }"
            @click="set_filter_click(null)
    ">Все</button>
    <button class="menu_button"
            :class="{ selected: store.filter == true }"
            @click="set_filter_click(true)">В наличии</button>
    <button class="menu_button"
            :class="{ selected: store.filter == false }"
            @click="set_filter_click(false)">Предзаказ</button>
    <button class="backet" @click="backet_click">
      <img :src="backet" class="backet_icon" alt="bad bar"/>
    </button>
    <div class="money" @click="open_money_types_click">
      {{store.money_type}} ᨆ
      <div class="other_money"
           @click="change_money_type('RUB')"
           v-if="(store.money_type != 'RUB') && (store.money_open)"
      >RUB</div>
      <div class="other_money"
           @click="change_money_type('EUR')"
           v-if="(store.money_type != 'EUR') && (store.money_open)"
      >EUR</div>
    </div>
  </div>
  <div class="shop">
    <div class="shop_item"
         v-for="(product, index) in products"
         :key="index"
         :product="product"
         :index="index"
    >
      <div class="shop_item_container"
           v-if="(store.filter==null)||store.filter==product.have"
           @click="details_click(product.id)"
      >
        <div class="shop_have" v-if="product.have">В наличии</div>
        <div class="shop_not_have" v-if="!product.have">Предзаказ</div>
        <img :src="product.image" alt="image" class="shop_item_img">
        <div class="shop_item_info">
          <p class="shop_item__name">{{product.name}}</p>
          <p class="shop_item__money" v-if="store.money_type=='RUB'">{{product.priceRUB}}₽</p>
          <p class="shop_item__money" v-if="store.money_type=='EUR'">{{product.priceEUR}}€</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.other_money{
  position: absolute;
  top: 50px;
  z-index: 1;
  background-color: var(--grey);
  padding: 2px 10px;
  border-radius: 20px;
}

.shop_have{
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 16px;
  font-size: 14px;
  border-radius: 20px;

  background-color: var(--red);
  color: var(--white);
}

.shop_item_container{
  width: 100%;
  display: flex;
  justify-content: center;
  flex-direction: column;
}

.shop_not_have {
  position: absolute;
  top: 12px;
  left: 12px;
  padding: 4px 16px;
  font-size: 14px;
  border-radius: 20px;

  background-color: var(--grey);
  color: var(--white);
}

.shop_item__money{
  color: var(--red);
  font-weight: bold;
  font-family: PT Mono, sans-serif;
}

.shop_item__name{
  font-weight: bold;
}

.shop_item_info{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  font-size: 16px;
}

.shop_item_img{
  height: auto;
  width: 100%;
  border-radius: 20px;
  border: 1px solid var(--grey)
}

.shop_item{
  width: 100%;
  height: auto;
  display: flex;
  justify-content: center;
  flex-direction: column;
  margin-top: 12px;
  position: relative;
}

.shop{
  display: flex;
  flex-direction: column;
}

.menu{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}

.menu_button{
  font-size: 12px;
  padding: 1% 4%;
  border-radius: 22px;
  background-color: var(--white);
  border: 1px solid var(--grey);
}

.menu_button.selected{
  background-color: var(--black);
  color: var(--white);
  border: 1px solid var(--black);
}

.backet_icon{
  width: 16px;
  height: 16px;
}

.backet{
  font-size: 12px;
  border-radius: 22px;
  background-color: var(--white);
  border: 1px solid var(--grey);
  padding: 6px;
  padding-bottom: 2px;
}

.money{
  display: flex;
  align-items: center;
  color: var(--text_grey);
}
</style>
