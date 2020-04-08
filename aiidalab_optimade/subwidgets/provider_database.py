import ipywidgets as ipw
import traitlets

from aiidalab_optimade.utils import (
    get_list_of_valid_providers,
    get_list_of_provider_implementations,
)


__all__ = ("ProvidersImplementations",)


class ProviderImplementationChooser(ipw.VBox):
    """List all OPTiMaDe providers and their implementations"""

    provider = traitlets.Dict(allow_none=True)
    database = traitlets.Tuple(traitlets.Unicode(), traitlets.Dict(allow_none=True))

    HINT = {"provider": "Select a provider", "child_dbs": "Select a database"}
    NO_OPTIONS = "No provider chosen"

    def __init__(self, debug: bool = False, **kwargs):
        self.debug = debug

        providers = []
        providers = get_list_of_valid_providers()
        providers.insert(0, (self.HINT["provider"], None))
        if self.debug:
            from aiidalab_optimade.utils import __optimade_version__

            local_provider = {
                "name": "Local server",
                "description": "Local server, running aiida-optimade",
                "base_url": f"http://localhost:5000/optimade/v{__optimade_version__.split('.')[0]}",
                "homepage": "https://example.org",
            }
            providers.insert(1, ("Local server", local_provider))
        implementations = [(self.NO_OPTIONS, None)]

        self.providers = ipw.Dropdown(
            options=providers,
            )
        self.child_dbs = ipw.Dropdown(
            options=implementations,
            disabled=True,
            )

        self.providers.observe(self._observe_providers, names="index")
        self.child_dbs.observe(self._observe_child_dbs, names="index")

        super().__init__(
            children=[self.providers, self.child_dbs],
            layout=ipw.Layout(min_width="24em"), **kwargs)

    def _observe_providers(self, change):
        """Update child database dropdown upon changing provider"""
        index = change["new"]
        self.child_dbs.disabled = True
        if index is None or self.providers.value is None:
            self.child_dbs.options = [(self.NO_OPTIONS, None)]
            self.child_dbs.disabled = True
            with self.hold_trait_notifications():
                self.providers.index = 0
                self.child_dbs.index = 0
        else:
            self.provider = self.providers.value
            implementations = get_list_of_provider_implementations(self.provider)
            implementations.insert(0, (self.HINT["child_dbs"], None))
            self.child_dbs.options = implementations
            self.child_dbs.disabled = False
            with self.hold_trait_notifications():
                self.child_dbs.index = 0
        self.child_dbs.disabled = False

    def _observe_child_dbs(self, change):
        """Update database traitlet with base URL for chosen child database"""
        index = change["new"]
        if index is None or self.child_dbs.options[index][1] is None:
            self.database = "", None
        else:
            self.database = self.child_dbs.options[index]

    def freeze(self):
        """Disable widget"""
        self.providers.disabled = True
        self.child_dbs.disabled = True

    def unfreeze(self):
        """Activate widget (in its current state)"""
        self.providers.disabled = False
        self.child_dbs.disabled = False

    def reset(self):
        """Reset widget"""
        with self.hold_trait_notifications():
            self.providers.index = 0
            self.providers.disabled = False

            self.child_dbs.options = [(self.NO_OPTIONS, None)]
            self.child_dbs.disabled = True


class ProviderImplementationSummary(ipw.HBox):
    """Summary/description of chosen provider and their database"""

    provider = traitlets.Dict(allow_none=True)
    database = traitlets.Dict(allow_none=True)

    def __init__(self, **kwargs):
        self.provider_summary = ipw.HTML()

        provider_section = ipw.VBox(
            children=[self.provider_summary],
            layout=ipw.Layout(
                max_width='48%', width="auto", height="auto", flex="1 1 auto"),
        )

        self.database_summary = ipw.HTML()
        database_section = ipw.VBox(
            children=[self.database_summary],
            layout=ipw.Layout(
                max_width='48%', width="auto", height="auto", flex="1 1 auto"),
        )

        super().__init__(
            children=[provider_section, database_section],
            layout=ipw.Layout(flex="1 1 auto"),
            **kwargs)

        self.observe(self._on_provider_change, names="provider")
        self.observe(self._on_database_change, names="database")

    def _on_provider_change(self, change):
        """Update provider summary, since self.provider has been changed"""
        new_provider = change["new"]
        self.database_summary.value = ""
        if new_provider is None:
            self.provider_summary.value = ""
        else:
            self._update_provider()

    def _on_database_change(self, change):
        """Update database summary, since self.database has been changed"""
        new_database = change["new"]
        if new_database is None:
            self.database_summary.value = ""
        else:
            self._update_database()

    def _update_provider(self):
        """Update provider summary"""
        html_text = f"""<h4>{self.provider.get('name', 'Provider')}</h4>
        <p style="line-height:1.2;">{self.provider['description']}</p>"""
        self.provider_summary.value = html_text

    def _update_database(self):
        """Update database summary"""
        html_text = f"""<h4>{self.database.get('name', 'Database')}</h4>
        <p style="line-height:1.2;">{self.database['description']}</p>"""
        self.database_summary.value = html_text

    def freeze(self):
        """Disable widget"""

    def unfreeze(self):
        """Activate widget (in its current state)"""

    def reset(self):
        """Reset widget"""
        self.provider = None


class ProvidersImplementations(ipw.HBox):
    """Combining chooser and summary widgets"""

    database = traitlets.Tuple(traitlets.Unicode(), traitlets.Dict(allow_none=True))

    def __init__(self, include_summary: bool = True, debug: bool = False, **kwargs):
        self.summary_included = include_summary
        self.debug = debug

        self.chooser = ProviderImplementationChooser(debug=self.debug)

        self.sections = [self.chooser]
        if self.summary_included:
            self.summary = ProviderImplementationSummary()
            self.sections.append(self.summary)

        if self.summary_included:
            super().__init__(
                children=[self.chooser, self.summary],
                **kwargs
                )
        else:
            super().__init__(children=[self.chooser], **kwargs)

        self.chooser.observe(self._update_database, names="database")
        if self.summary_included:
            self.chooser.observe(self._update_provider, names="provider")

    def _update_database(self, change):
        """Patch database through to own traitlet and pass info to summary"""
        self.database = change["new"]
        if self.summary_included:
            self.summary.database = self.database[1]

    def _update_provider(self, change):
        """Pass information to summary"""
        self.summary.provider = change["new"]

    def freeze(self):
        """Disable widget"""
        for widget in self.sections:
            widget.freeze()

    def unfreeze(self):
        """Activate widget (in its current state)"""
        for widget in self.sections:
            widget.unfreeze()

    def reset(self):
        """Reset widget"""
        for widget in self.sections:
            widget.reset()
