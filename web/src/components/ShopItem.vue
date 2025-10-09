<script setup lang="ts">
import {store} from "../store.js";
import {products} from "../types/Data.ts";
import {useRouter} from "vue-router";
const router = useRouter()

let product = products[store.current_product]
let len = product.images.length;

const change_money_type = (value: string) => {
  store.money_type = value
  store.money_open = false
}

const left_click = () => {
  store.index = (len + store.index-1)%len
}

const right_click = () => {
  store.index = (store.index+1)%len
}

const open_money_types_click = () => {
  store.money_open = !store.money_open
}

const back_click = () => {
  store.money_open = false
  router.back()
}

const change_index_size_click = (index: number) => {
  store.index_size = index
}

const add_to_backet_click = () => {
  if (product.id == 1) {
    store.rubaska_count[store.index_size] += 1
  } else if (product.id == 2) {
    store.rain_count[store.index_size] += 1
  } else if (product.id == 0) {
    store.flyaga_count[store.index_size] += 1
  }
}

</script>

<template>
  <div class="shop_item">
    <div class="back" @click="back_click">←</div>
    <div class="money_type" @click="open_money_types_click">{{store.money_type}} ᨆ</div>
    <div class="other_money"
         @click="change_money_type('RUB')"
         v-if="(store.money_type != 'RUB') && (store.money_open)"
    >RUB</div>
    <div class="other_money"
         @click="change_money_type('EUR')"
         v-if="(store.money_type != 'EUR') && (store.money_open)"
    >EUR</div>
    <img :src="product.images[store.index]" class="image">
    <div class="left" @click="left_click()">⟨</div>
    <div class="right" @click="right_click()">⟩</div>
    <div class="info">
      <div class="title">
        <div class="title_name">{{product.name}}</div>
        <div class="price"
             v-if="store.money_type == 'RUB'"
        >{{product.priceRUB}}₽</div>
        <div class="price"
             v-if="store.money_type == 'EUR'"
        >{{product.priceEUR}}€</div>
      </div>
      <div class="description"
           v-for="(desc, index) in product.description"
           :key="index"
           :desc="desc"
           :index="index"
      >
        {{desc}}
        <br v-if="desc==''"/>
      </div>
    </div>
    <div class="footer">
      <div
          class="sizes"
          v-if="product.sizes!=null"
      >
        <div class="size"
             v-for="(size, index) in product.sizes"
             :key="index"
             :size="size"
             :index="index"
             :class="{ selected: store.index_size == index}"
             @click="change_index_size_click(index)"
        >
          {{size}}
        </div>
      </div>
      <div class="types"
           v-if="product.types!=null"
      >
        <div class="type">
          <div>{{product.types[store.index_size]}}</div>
          <div class="sign">ᨆ</div>
        </div>
      </div>
      <div class="button" @click="add_to_backet_click()">
        В корзину
      </div>
    </div>
  </div>
</template>

<style scoped>
.type{
  color: var(--grey_desc);
  width: calc(100% - 40px);
  padding: 8px 20px;
  border: 1px solid var(--grey);
  font-size: 12px;
  justify-content: space-between;
  display: flex;
  flex-direction: row;
  border-radius: 22px;
}

.button{
  width: 100%;
  background-color: var(--black);
  color: white;
  font-size: 14px;
  text-align: center;
  padding: 12px 0;
  margin: 20px 0;
  border-radius: 22px;
}

.sizes{
  display: flex;
  flex-direction: row;
  gap: 1%;
  justify-content: center;
}

.size{
  padding: 2% 8px ;
  border-radius: 22px;
  border: 1px solid var(--grey);
}

.size.selected {
  background-color: var(--black);
  color: white;
  border: 1px solid var(--black);
}

.footer{
  position: fixed;
  bottom: 0;
  background-color: var(--white);
  width: calc(100% - 40px);
  max-width: 460px;
  padding: 20px;
}

.description{
  color: var(--grey_desc);

}

.price{
  color: var(--red);
  font-family: PT Mono, sans-serif;
}

.title{
  display: flex;
  justify-content: space-between;
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 12px;
}

.info{
  max-width: 100%;
  min-height: 100vh;
  border-radius: 32px;
  background-color: var(--white);
  position: relative;
  top: -32px;
  padding: 20px;
}

.other_money{
  position: absolute;
  top: 50px;
  right: 20px;
  z-index: 1;
  background-color: var(--grey);
  padding: 8px 0;
  width: 66px;
  border-radius: 20px;
  font-size: 12px;
  display: flex;
  justify-content: center;
}

.back{
  color: var(--white);
  background-color: var(--black);
  position: absolute;
  display: flex;
  width: 28px;
  height: 28px;
  border-radius: 22px;
  justify-content: center;
  align-items: center;
  top: 20px;
  left: 20px;
}

.money_type{
  color: var(--white);
  background-color: var(--black);
  position: absolute;
  top: 20px;
  right: 20px;
  padding: 8px 12px;
  font-size: 12px;
  border-radius: 22px;
}

.shop_item{
  width: 100%;

}

.left{
  color: var(--text_grey);
  font-size: 50px;
  position: absolute;
  top: 150px;
  left: 20px;
}

.right{
  color: var(--text_grey);
  font-size: 50px;
  position: absolute;
  top: 150px;
  right: 20px;
}

.image{
  width: 100%;
}
</style>