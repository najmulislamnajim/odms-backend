from app.db.base_class import Base  # noqa: F401

from app.models.attendance import RdlAttendance #noqa F401
from app.models.conveyance import RdlConveyance #noqa F401 
from app.models.customer_visit import RdlCustomerVisit #noqa F401 
from app.models.customer import RplCustomerList, RplCustomerSalesOrg, RplCustomerTerritory, RplCustomerRouteHistory, RdlCustomerLocation  # noqa: F401
from app.models.delivery_collection import RdlDeliveryCollection #noqa F401
from app.models.delivery_info_sap import RdlDeliveryInfoSap #noqa F401
from app.models.delivery_return_item import RdlDeliveryReturnItem #noqa F401
from app.models.depot import RdlDepotList  # noqa: F401
from app.models.material import RplMaterialList #noqa F401
from app.models.overdue import RdlOverdue #noqa F401
from app.models.payment import RdlPaymentHistory #noqa F401
from app.models.route import RdlRouteList, RdlRouteHistory  # noqa: F401
from app.models.sales_info_sap import RplSalesInfoSap #noqa F401
from app.models.sales_user import RplUserList #noqa F401
from app.models.user_credential import RdlUserCredential  # noqa: F401
from app.models.user import RdlUserList, RdlUserHistory  # noqa: F401
from app.models.sync_log import RdlSyncLog  # noqa: F401
from app.models.customer_sync_reject import RdlCustomerSyncReject  # noqa: F401