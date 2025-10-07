import { createRouter, createMemoryHistory } from 'vue-router'

import Shop from './components/Shop.vue'
import Backet from './components/Backet.vue'
import ShopItem from './components/ShopItem.vue'
import Delivery from './components/Delivery.vue'

const routes = [
    {
        path: '/',
        name: 'Shop',
        component: Shop
    },
    {
        path: '/details',
        name: 'ShopItem',
        component: ShopItem
    },
    {
        path: '/backet',
        name: 'Backet',
        component: Backet
    },
    {
        path: '/delivery',
        name: 'Delivery',
        component: Delivery
    }
]

const router = createRouter({
    history: createMemoryHistory(),
    routes,
    scrollBehavior(to, from, savedPosition) {
        return { left: 0, top: 0 };
    },
})

export default router