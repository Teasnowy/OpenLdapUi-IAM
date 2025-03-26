
export interface actionData {
    "id_abs_list": Array<Array<string>>,
    "id_abs": Array<string>
    "id": string,
    "link": string,
    "note": string,
    "title": string,
    "type_fri": string,
    "type_sec": string
}

export interface logInter {
    env: string,
    type: string,
    date: string,
    sw_time_check: boolean,
    time_start: string,
    time_stop: string,
    deployment: {
        name: string,
        pods: {
            [key: string]: {
                host: string,
                sys_cn: string,
                sys_en: string,
            }
        }
    },
    log_re: string,
    sw_a: number,
    token: string,
    files: {
        [key: string]: OneFileInfo
    },
    count_size: string,
    count_size_init: number,
    passwd_zip: string,
    disk_usage_percent?: number,
    disk_usage_free: number,
    down_link_count: DownLinkCount

}

// 冷日志页面后端返回的所有微服务信息
export interface resAppObj {
    [key:string]: {
        [key:string]: {
            host: string,
            sys_cn: string,
            sys_en: string,
        }
    }
}

export interface deployInter {
    name: string,
    pods: {}
}

export interface listFileInfo {
    count_size: string,
    count_size_init: number,
    passwd_zip: string,
    files: {},
    disk_usage_percent: number
    disk_usage_free: number
}

export interface OneFileInfo {
    size?: string,
    url?: string,
    log_path?: string,
    log_env?: string,
    log_date?: string,
    log_service?: string
}


export interface DownLinkCount {
    url?: string,
    file_name?: string,
    file_oss_path?: string,
    file_size?: string,
    list_log_line?: [],
    log_line_len?: number
}

// 获取首页告警信息的格式
export interface homeAlert {
    info:string,
    title:string,
    src:string
}

// 包含首页所有link的集合
export interface allLinks{
    on: homeLinks,
    off: homeLinks,
    on_ascader: homeLinksCascader[],
    off_ascader: homeLinksCascader[],
}


// 首页快捷方式的后端返回格式
export interface homeLinks {
    [key: string]: {
        [key: string]: Array<{
            id: string
            title: string,
            link: string,
            note: string
        }>
    },
}

// 首页快捷方式, 后端为了方便级联选择器数据格式额外返回的格式
export interface homeLinksCascader {
    value: string,
    label: string,
    children: Array<{
        value: string,
        label: string,
        children: Array<{
            value: string,
            label: string,
        }>
    }>
}

// helm页面: 后端返回的helm数据格式
export interface helmAll {
    downLink?: string,
    status_modify?: boolean,
    status_deploy?: boolean,
    servers: {
        [key: string]: {
            env_name_zh: string,
            charts: {
                [key: string]: Array<string>
            }
        }
    }
    yamls: {
        [key: string]: string
    }
}

// helm页面: 向后端发起请求时, 参数信息
export interface helmRequest {
    action: "check" | "modify" | "getyaml" | "deploy" | "",
    chartInfo: {
        env: string,
        server: string,
        version: string
    },
    yamls: {
        [key: string]: string
    },
    // switch_deployk8s: boolean
}

// 营销平台前端同步页面向后端请求的参数
export type opts_actions = "insert" | "update" | "delete"
export interface dmpHtml_request {
    type: "init" | "check" | "async",
    list_actions?: opts_actions[],
    list_tables?: Array<string>
}

// 营销平台前端同步页面后端的返回
export interface dmpHtml_return {
    list_actions_all? : Array<string>,
    list_tables_all?: Array<string>,
    // 源库名
    db_name_source?: string,
    // 目的库名
    db_name_target?: string,
    // 对比两个库的结果
    result_check?: {
        // 目标表
        info_source?: [],
        // 源表
        info_target?: [],
        // 唯一索引冲突的信息
        err_uniqueIndex?: [],
        // 即将执行的sql列表
        list_all_sql?: [],
    },
    result_async?: {
        'OK': string,
        'ERR': string,
    }

}

// 经典的级联选择器数据结构, 无限套层, 引用时请加中括号
export interface cascader_select {
    label: string,
    value: string,
    children: cascader_select[]
}


// 发送请求时的数据
export interface goodsData {
    env: string,
    list_product_number: Array<string>,
    action: 'check' | 'sync' | ""
}


// check动作时后端的返回
export interface goodsResCheck {
    [key:string]: goodsResCheck_key
}

export interface goodsResCheck_key {
    "n_goods_product": number,
    "n_stock_sku": number,
    "n_cost_err": number,
    "n_market_err": number,
    "n_name_err": number,
    "n_sku_num_unsync": number,
    "init_cost_price": number,
    "info_goods_product": info_goods_product,
    "list_info_product": Array<info_goods_product>,
    "list_tmp": Array<string>,
    "list_sku_unsync_number": Array<string>,
    "list_sku_unsync_name": Array<string>,
}

export interface info_goods_product {
    "type": string,
    "name": string,
    "init_product_name": string,
    "id": string,
    "cost_price": string,
    "init_cost_price": string,
    "market_price": string,
    "init_market_price": string,
    "date_create": string,
    "date_update": string
}


// goods库product表的结构
interface goods_product {
    "ID": 6391333,
    "PRODUCT_NUMBER": string,
    "PRODUCT_NAME": string,
    "DESCRIPTION": string,
    "KEYWORD": string,
    "CATEGORY_CLASS_1": string,
    "CATEGORY_CLASS_2": string,
    "CATEGORY_CLASS_3": string,
    "CATEGORY_CLASS_4": string,
    "SHORE_STYLE": string,
    "TOE_TYPE": string,
    "HEEL_TYPE": string,
    "UPPER_MATERIAL": string,
    "PRODUCT_SERIES": string,
    "IS_PRESALE": number,
    "PRESALE_START_DATE": string,
    "PRESALE_END_DATE": string,
    "YEAR_CODE": string,
    "SEASON_CODE": string,
    "BRAND_CODE": string,
    "SUPPLIER_CODE": string,
    "SIZE_KIND": string,
    "SALE_NUM": string,
    "USE_TYPE": string,
    "IS_COMPLETE": number,
    "COST_PRICE": string,
    "DATE_CREATED": string,
    "CREATED_BY": string,
    "UPDATED_BY": string,
    "DATE_UPDATED": string,
    "IS_DELETED": number,
    "IS_PUBLISH": number,
    "DEVELOP_CODE": string,
    "IS_PUBLISH_DOU_DIAN": number
}


// stock库kc_sku_attribute表的结构
interface stock_kc_sku_attribute {
    "ID": number,
    "STOCK_PRODUCT_TYPE": string,
    "PRODUCT_YEAR": string,
    "PRODUCT_SEASON": string,
    "PRODUCT_NAME": string,
    "PRODUCT_COLOR": string,
    "PRODUCT_SIZE": string,
    "SKU_CODE": string,
    "sap_category_code1": string,
    "sap_category_code2": string,
    "sap_category_code3": string,
    "sap_category_code4": string,
    "brandName": string,
    "product_code": string,
    "category_code": string,
    "sku_name": string,
    "valid_flag": string,
    "date_created": string,
    "date_updated": string,
    "supplier_id": number,
    "supplier_name": string,
    "brand_id": string,
    "MERCHANT_ID": string,
    "MARKET_PRICE": string,
    "CREATED_BY": string,
    "UPDATED_BY": string,
    "product_code_color": string,
    "SIZE_KIND": string,
    "COST_PRICE": string
}


// 日期范围的快捷选项
export const dateRangeShortcuts = [
    {
        text: '15分钟内',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setMinutes(start.getMinutes()-15)
            return [start, end]
        },
    },
    {
        text: '半小时内',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setMinutes(start.getMinutes()-30)
            return [start, end]
        },
    },
    {
        text: '1小时内',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(start.getHours()-1)
            return [start, end]
        },
    },
    {
        text: '2小时内',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(start.getHours()-2)
            return [start, end]
        },
    },
    {
        text: '今日内',
        value: () => {
            const end = new Date()
            const start = new Date()
            start.setHours(0,0,0,0)
            return [start, end]
        },
    },
]