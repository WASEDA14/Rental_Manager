from services.dashboard_service import get_dashboard_stats

class DashboardController:
    def __init__(self, view=None):
        self.view = view
    
    def refresh_data(self):
        try:
            stats = get_dashboard_stats()
            self.view.update_room_card(
                occupied=stats['occupied_rooms'],
                total=stats['total_rooms']
            )
            self.view.update_tenant_card(count=stats['total_tenants'])
            self.view.update_payment_card(amount=stats['monthly_payment'])
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
