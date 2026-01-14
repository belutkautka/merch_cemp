import { reactive } from 'vue'
import {products} from "./types/Data.js";

export const store = reactive({
    money_type: "RUB",
    current_product: 0,
    filter: null,
    money_open: false,
    index: 0,
    index_size: 0,
    selected_height: "158-164", // выбранный рост для рубашки
    //order
    rubaska_count: [0,0,0,0,0,0,0,0,0],
    rain_ML_count: [0],
    rain_XLXXL_count: [0],
    flyaga_count: [0,0,0],

    // Получатель
    recipient_type: "me", // "me" или "gift"

    // Доставка
    delivery_type: "Ближайший ПВЗ",
    delivery_open: false,
    selected_delivery_id: "pvz",
    delivery_price: 0,

    // Поля для ПВЗ
    pvz_city: "",
    pvz_link: "",
    pvz_recipient_name: "",
    pvz_recipient_phone: "",

    // Поля для курьера по Екатеринбургу
    courier_address: "",
    courier_comment: "",
    courier_recipient_name: "",

    // Поля для Worldwide
    worldwide_country: "",
    worldwide_city: "",
    worldwide_zip: "",
    worldwide_address: "",
    worldwide_phone: "",
    worldwide_comment: "",
    worldwide_recipient_name: "",

    // Поля для "Другое"
    other_comment: "",
})