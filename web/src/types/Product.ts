export interface Product {
    id: number
    images: string[]
    image: string
    name: string
    description: string[]
    priceRUB: number
    sizes: string[]|null
    have: boolean
}