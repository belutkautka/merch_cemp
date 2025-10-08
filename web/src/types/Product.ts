export default interface Product {
    id: number
    images: string[]
    image: string
    name: string
    description: string[]
    priceRUB: number
    priceEUR: number
    sizes: string[]|null
    types: string[]|null
    have: boolean
}