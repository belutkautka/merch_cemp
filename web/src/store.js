import { reactive } from 'vue'
import {products} from "./types/Data.js";

export const store = reactive({
    money_type: "RUB",
    current_product: 0,
    filter: null
})