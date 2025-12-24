from services.dashboard_service import get_dashboard_stats

class DashboardController:
    def __init__(self, view=None):
        self.view = view
    
    def refresh_data(self):
        try:
            stats = get_dashboard_stats()
            self.view.reload_room_card(
                occupied=stats['occupied_rooms'],
                total=stats['total_rooms']
            )
            self.view.reload_tenant_card(count=stats['total_tenants'])
            self.view.reload_payment_card(paid=stats['paid_bills'], total=stats['total_bills'])
        except Exception as e:
            print(f"Lỗi reload: {e}")
