import { reactive } from 'vue'
import {products} from "./types/Data.js";

export const store = reactive({
    money_type: "EUR",
    current_product: 0,
    filter: null,
    money_open: false,
    index: 0,
    index_size: 0,
    //order
    rubaska_count: [0,0,0,0,0,0,0,0],
    rain_count: [0,0],
    flyaga_count: [0,0,0]
})