import {global_window} from '@/api/def_feedback'
import {getServer} from "@/api/def_servers";


// 图片的blob对象转为base64, 需要await
export function blob_to_base64(blob:Blob|null|undefined) {

    // upload.value?.clearFiles()
    return new Promise((resolve, reject) => {
        if (!(blob instanceof Blob)) {
            console.log(typeof blob, blob)
            if (!blob) {
                global_window("error", "你似乎没有选择或上传图片")
            } else {
                global_window("error", "图片未能成功转化为blob格式")
            }
            reject("")
        }

        const reader = new FileReader();

        reader.onloadend = () => {
            resolve(reader.result as string);  // 返回 Base64 编码
        };
        reader.onerror = () => {
            global_window("error", "读取文件失败")
            reject(new Error('读取文件失败'));
        };
        // 读取 Blob 为 Data URL（Base64编码）
        reader.readAsDataURL(blob!);
    });
}

// 解析jwt的前两段
export function parseJWT(token:string) {
    if (!token) {
        return ""
    }
    // 拆分 JWT 字符串
    const parts = token.split('.');
    if (parts.length !== 3) {
        // throw new Error('jwt格式不对');
        console.log('jwt格式不对')
        return ""
    }

    // 解码 Base64Url 为普通 Base64
    const decodeBase64Url = (str:string) => {
        // 用 Base64Url 转为标准 Base64
        str = str.replace(/-/g, '+').replace(/_/g, '/');
        // 补充 Base64 padding
        while (str.length % 4) {
            str += '=';
        }
        return atob(str); // 使用浏览器的 atob() 解码 Base64
    };

    // 解码 Header 和 Payload 部分
    // const header = JSON.parse(decodeBase64Url(parts[0]));
    return JSON.parse(decodeBase64Url(parts[1]))
}

// 将图片的base64再次压缩并裁剪为正方形(居中裁剪), base64Str图片的base64, targetSizeKB目标大小, 单位KB
export function compressAndCropBase64Image(base64Str:string, targetSizeKB:number) {
    return new Promise((resolve, reject) => {
        // 创建图片对象
        const img = new Image();
        img.src = base64Str;

        // 图片加载完成后的处理
        img.onload = function() {
            // 获取图片原始宽高
            const width = img.width;
            const height = img.height;

            // 裁剪正方形的边长（以较小的一边为准）
            const size = Math.min(width, height);

            // 创建 canvas 元素
            const canvas = document.createElement('canvas');
            const ctx:any = canvas.getContext('2d');

            // 计算裁剪区域的起始点（使裁剪区域居中）
            const sx = (width - size) / 2;
            const sy = (height - size) / 2;

            // 设置 canvas 尺寸为裁剪后的正方形尺寸
            canvas.width = size;
            canvas.height = size;

            // 将图片裁剪并绘制到 canvas 上
            ctx.drawImage(img, sx, sy, size, size, 0, 0, size, size);

            // 压缩图片的质量，初始为 0.9
            let quality = 0.9;
            let base64Compressed = canvas.toDataURL('image/jpeg', quality);

            // 估算图片大小，并逐步降低质量直到符合目标大小
            let imageSizeKB = (base64Compressed.length * 3 / 4) / 1024; // Base64 编码大小转换为 KB

            while (imageSizeKB > targetSizeKB && quality > 0.1) {
                quality -= 0.05;  // 每次减少 5%
                base64Compressed = canvas.toDataURL('image/jpeg', quality);
                imageSizeKB = (base64Compressed.length * 3 / 4) / 1024; // 更新图片大小
            }

            // 返回压缩后的 Base64 编码
            resolve(base64Compressed);
        };

        img.onerror = function(err) {
            reject('图片加载失败: ' + err);
        };
    });
}