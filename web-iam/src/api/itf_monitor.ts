// 获取所有后台任务的返回信息
export type res_crontab_list = res_crontab_once[]
interface res_crontab_once {
    args: any[];
    func: string;
    id: string;
    name: string;
    next_run_time: string;
    next_run_time_strftime: string;
    trigger: string;
}