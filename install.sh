#!/bin/bash
# 安装和运行脚本

echo "================================"
echo "代理池系统安装和运行"
echo "================================"
echo ""

# 检查Python版本
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "Python版本: $python_version"

if [ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]; then
    echo "错误: 需要Python 3.8或更高版本"
    exit 1
fi

echo ""
echo "1. 安装依赖包..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

echo ""
echo "2. 测试导入模块..."
python3 -c "from proxy_pool import ProxyPool; from optimized_fetcher import OptimizedProxyFetcher; print('✓ 模块导入成功')"

if [ $? -ne 0 ]; then
    echo "错误: 模块导入失败"
    exit 1
fi

echo ""
echo "3. 测试代理获取器..."
python3 test_fetcher.py

echo ""
echo "================================"
echo "安装完成！"
echo "================================"
echo ""
echo "使用方法:"
echo "  运行一次:      python3 proxy_manager.py [GitHub_TOKEN]"
echo "  持续运行:      python3 proxy_manager.py continuous [GitHub_TOKEN]"
echo "  测试获取器:    python3 test_fetcher.py"
echo ""
echo "更多详细信息请查看 README.md"
