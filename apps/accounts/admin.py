from django.contrib import admin
from .models import User
from django.urls import path
from django.shortcuts import render
import psutil
import matplotlib.pyplot as plt
import io
import base64



class SystemMonitorAdmin(admin.AdminSite):
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('system-monitor/', self.admin_view(self.system_monitor), name='system-monitor'),
        ]
        return custom_urls + urls

    def system_monitor(self, request):
        # 获取 CPU 和内存使用情况
        cpu_usage = psutil.cpu_percent(interval = 1)
        memory_usage = psutil.virtual_memory().percent

        # 创建包含三个子图的图形，1行3列
        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        # 在第一个子图中绘制CPU饼图
        cpu_pie_labels = ['CPU Used', 'CPU Free']
        cpu_pie_sizes = [cpu_usage, 100 - cpu_usage]
        colors = ['#FFA500', '#90EE90']
        axs[1].pie(cpu_pie_sizes, labels = cpu_pie_labels, autopct='%1.1f%%', startangle = 90, colors = colors)
        axs[1].set_title('CPU Usage')

        # 在第二个子图中绘制内存饼图
        memory_pie_labels = ['Memory Used', 'Memory Free']
        memory_total = psutil.virtual_memory().total
        memory_used = psutil.virtual_memory().used
        memory_free = memory_total - memory_used
        memory_pie_sizes = [memory_used / memory_total * 100, memory_free / memory_total * 100]
     
        axs[2].pie(memory_pie_sizes, labels = memory_pie_labels, autopct='%1.1f%%', startangle = 90, colors = colors)
        axs[2].set_title('Memory Usage')

        # 在第三个子图中绘制柱状图（原有的柱状图内容）
        labels = ['CPU Usage', 'Memory Usage']
        values = [cpu_usage, memory_usage]
        axs[0].bar(labels, values, color=['#FFA500', '#FFA500'])
        axs[0].set_title('System Monitor - Bar')
        axs[0].set_ylabel('Percentage (%)')
        bar = axs[0].bar(labels, values, color=['#FFA500', '#FFA500'])
        axs[0].bar_label(bar)

        # 将整个图形转换为 base64 编码
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

        # 渲染模板
        return render(request, 'admin/system_monitor.html', {
            'image_base64': image_base64
        })
# 注册自定义 AdminSite
custom_admin_site = SystemMonitorAdmin(name='customadmin')


custom_admin_site.register(User)

admin.site.register(User)
