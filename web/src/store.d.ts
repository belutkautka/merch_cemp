export const store: {
    money_type: string;
    current_product: number;
    filter: boolean | null;
    money_open: boolean;
    index: number;
    index_size: number;
    selected_height: string;
    rubaska_count: number[];
    rain_ML_count: number[];
    rain_XLXXL_count: number[];
    flyaga_count: number[];

    // Получатель
    recipient_type: string;

    // Доставка
    delivery_type: string;
    delivery_open: boolean;
    selected_delivery_id: string;
    delivery_price: number;

    // Поля для ПВЗ
    pvz_city: string;
    pvz_link: string;
    pvz_recipient_name: string;
    pvz_recipient_phone: string;

    // Поля для курьера по Екатеринбургу
    courier_address: string;
    courier_comment: string;
    courier_recipient_name: string;

    // Поля для Worldwide
    worldwide_country: string;
    worldwide_city: string;
    worldwide_zip: string;
    worldwide_address: string;
    worldwide_phone: string;
    worldwide_comment: string;
    worldwide_recipient_name: string;

    // Поля для "Другое"
    other_comment: string;
}
