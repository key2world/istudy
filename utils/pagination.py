class Pagination:
    def __init__(self, request, data_length, pre_num=10, max_show=10):
        try:
            page = int(request.GET.get("page", 1))  # 如果url上没有这个参数，则默认值1
            if page <= 0:
                page = 1
        except Exception:
            page = 1

        # 每页显示的数据条数  内容的多少
        # pre_num = 10

        # url上的参数  一个字典
        querydict = request.GET.copy()  # 一个可编辑的深拷贝字典

        # 就是显示的内容
        # 切片的起始值
        self.start = (page - 1) * pre_num
        # 切片的终止值
        self.end = page * pre_num

        # 总的页码数
        # total_num = len(users) / pre_num
        # divmod 有两个返回值，分别是整除的结果，取余的结果
        total_num, more = divmod(data_length, pre_num)
        if more:
            total_num += 1

        # 要显示的页码数
        # max_show = 10
        # 页码条中间的那个数
        half_show = max_show // 2

        # 如果总的页码数还没有要显示的页码数多 就显示总的页码数
        if total_num <= max_show:
            # 页码的起始值
            page_start = 1
            # 页码的终止值
            page_end = total_num
        else:
            # 就是为了页码条永远等于要显示的页码数
            page_start = page - half_show
            page_end = page + half_show - 1
            if page_start <= 0:
                page_start = 1
                page_end = max_show

            elif page_end > total_num:
                page_start = total_num - max_show + 1  # 小bug 不然就会出现11个页码数
                page_end = total_num
        page_list = ['<nav aria-label="Page navigation"><ul class="pagination pagination-lg">']
        if page == 1:
            page_list.append(
                '<li class="disabled"><a><span aria-hidden="true">&laquo;</span></a></li>')  # 如果上一页没有了 就把这个标签禁用掉
        else:
            querydict["page"] = page - 1
            page_list.append(
                '<li><a href="?{}" aria-label="Previous"><span aria-hidden="true">&laquo;</span></a></li>'.format(
                    querydict.urlencode()))  # 上一页

        for i in range(page_start, page_end + 1):
            querydict["page"] = i  # 给字典中加入键值对
            if i == page:  # 当前页码特殊显示
                page_list.append('<li class="active"><a href="?{}">{}</a></li>'.format(querydict.urlencode(), i))
            else:
                page_list.append('<li><a href="?{}">{}</a></li>'.format(querydict.urlencode(), i))
        if page == total_num:
            page_list.append(
                '<li class="disabled"><a><span aria-hidden="true">&raquo;</span></a></li>')  # 没有下一页禁用标签
        else:
            querydict["page"] = page + 1
            page_list.append(
                '<li><a href="?{}" aria-label="Previous"><span aria-hidden="true">&raquo;</span></a></li>'.format(
                    querydict.urlencode()))  # 下一页
        page_list.append('</ul></nav>')

        self.page_html = "".join(page_list)
