from services.dashboard_service import get_dashboard_stats

class DashboardController:
    def __init__(self, view=None):
        self.view = view
    
    def refresh_data(self):
        """
        Fetch the latest dashboard data and update the view
        """
        try:
            stats = get_dashboard_stats()
            
            # Update the view with the latest data
            self.view.update_room_card(
                occupied=stats['occupied_rooms'],
                total=stats['total_rooms']
            )
            self.view.update_tenant_card(count=stats['total_tenants'])
            # Payment card update removed as the UI element is disabled
            
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
