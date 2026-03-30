from app.plugins.manager import PluginManager

# Global plugin manager instance
plugin_manager = PluginManager()
plugin_manager.discover_plugins()
