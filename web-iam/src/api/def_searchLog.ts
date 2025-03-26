import {getServer} from '@/api/def_servers'
import type {logInter} from '@/api/itf_devops'


// 获取环境名
export function getEnv(){
    return {
        "生产": "aliprod"
    }
}


// 获取操作类型
export function getAction(){
    return {
        "下载完整聚合包": "down_all",
        "查询关键字": "check",
        "下载某时间段原文": "down_region",
    }
}


// 获取k8s的微服务列表
export function getK8sInfo(time:string, env:string){
    return getServer("/api/get/k8sinfo",{
        date: time,
        env: env
    })
}


// 查询指定日期指定日志列表
export function getLogInfo(info:any){
    return getServer("/api/get/loginfo", info)
}

// 聚合当天日志并返回下载链接
export function getLogTar(info:any){
    return getServer("/api/get/filemodify", info)
}


// 转换时间格式, 但是设计了一个兜底时间
export function secondsToString(seconds:number, ismax:boolean=true) {
    // 如果小于20 , 则强制等于20
    if (seconds < 20 && ismax) {
        seconds = 20
    }

    let y = Math.floor(seconds / 31536000);
    let d = Math.floor((seconds % 31536000) / 86400);
    let h = Math.floor(((seconds % 31536000) % 86400) / 3600);
    let m = Math.floor((((seconds % 31536000) % 86400) % 3600) / 60);
    let s = Math.floor((((seconds % 31536000) % 86400) % 3600) % 60);

    let result = '';
    if (y) result += y + "年";
    if (d) result += d + "天";
    // 这里是如果数字小于10则前面加0, 目前不加
    if (h) {
        // h<10?result += '0'+h + "小时":result += h + "小时";
        result += h + "小时";
    }
    if (m) {
        // m<10?result += '0'+m + "分":result += m + "分";
        result += m + "分钟";
    }
    if (s) {
        // s<10?result += '0'+s + "秒":result += s + "秒";
        result += s + "秒";
    }

    return result;
}

// export const useResOpts = defineStore('res_opts', {
//     state() {
//
//         let dict:logInter = {
//             env: "",
//             type: "",
//             date: "",
//             sw_time_check: false,
//             time_start: "",
//             time_stop: "",
//             deployment: {
//                 name: "",
//                 pods: {}
//             },
//             log_re: '',
//             sw_a: 0,
//             token: '',
//             files: {},
//             count_size: '',
//             count_size_init: 0,
//             passwd_zip: '',
//             disk_usage_percent: 0,
//             down_link_count: {}
//         }
//         return {
//             dict
//         }
//     }
//
// })


// 判断当前请求用的参数是否合法的api
export function queryJudge_currency(dict:logInter) {
    // 判断类型
    let type_input = dict.type

    // 读取变量
    let {
        sw_time_check,
        time_start,
        time_stop,
        deployment: {
            name,
            pods
        },
        log_re,
        disk_usage_percent,
        disk_usage_free,
        count_size_init,
        count_size,
    } = dict

    // 判断整体是否合法
    let status_check = true
    // 如果不合法, 提示词是什么
    let list_res_crime = []


    // 通用判断
    if (!name) {
        list_res_crime.push("没有指定微服务名字")
    }
    if (Object.keys(pods).length == 0) {
        list_res_crime.push("没有指定pod名字")
    }

    if (disk_usage_percent) {
        if (disk_usage_percent > 90) {
            list_res_crime.push("后端磁盘爆炸了, 请报告给运维")
        }
    }
    // 剩余磁盘空间必须大于文件总大小解压后的1.5倍, 解压按15倍算
    console.log("剩余空间: "+disk_usage_free+", 文件总大小"+count_size_init)
    if (disk_usage_free < (count_size_init * 15 * 1.5)) {
        list_res_crime.push("剩余磁盘空间不满足"+count_size+"解压后的空间")
    }

    // 各选项的判断
    // 如果选择的是下载日志原文
    if (type_input == "down_all") {
        // 如果选择的是检查关键字
    } else if (type_input == "check") {
        // 关键字长度不能小于12
        if (log_re.length < 12) {
            list_res_crime.push("关键字长度不得小于12")
        }
        // 勾选时间段时没选择开始时间
        if (sw_time_check && !time_start) {
            list_res_crime.push("没选开始时间点")
        }
        // 勾选时间段时没选择结束时间
        if (sw_time_check && !time_stop) {
            list_res_crime.push("没选结束时间点")
        }
        // 如果选择的是下载时间区间
    } else if (type_input == "down_region") {
        // 没选择开始时间
        if (!time_start) {
            list_res_crime.push("没选开始时间点")
        }
        // 没选择结束时间
        if (!time_stop) {
            list_res_crime.push("没选结束时间点")
        }
    }


    // 判断整体是否合法
    if (list_res_crime.length == 0) {
        status_check = false
    }

    return {status_check, list_res_crime}
}