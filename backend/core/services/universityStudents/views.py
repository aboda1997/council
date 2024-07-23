from core.utils.responses import ServiceResponse
from core.utils.views import ServiceAPIView

from .controller import get_students_list


class StudentsList(ServiceAPIView):
    def post(self, request):
        page = request.data.get('page', 0)
        per_page = request.data.get('perPage', 50)
        data = get_students_list(request.data, page, per_page)
        return ServiceResponse(**data)
