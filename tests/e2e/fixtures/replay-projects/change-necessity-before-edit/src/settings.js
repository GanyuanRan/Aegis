export const DEFAULT_THEME = "system";

export function normalizeTheme(value) {
  return value || DEFAULT_THEME;
}

export function renderThemeLabel(settings) {
  return normalizeTheme(settings.theme);
}
