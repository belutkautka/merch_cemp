import { reactive } from 'vue'
import {products} from "./types/Data.js";

export const store = reactive({
    money_type: "RUB",
    current_product: 0,
    filter: null,
    money_open: false,
    index: 0,
    index_size: 0,
    //order
    rubaska_count: [0,0,0,0,0,0,0,0],
    rain_ML_count: [0],
    rain_XLXXL_count: [0],
    flyaga_count: [0,0,0],

    // Доставка
    delivery_type: "Кэмп",
    delivery_open: false,
    selected_delivery_id: "camp",
    delivery_price: 0,
})