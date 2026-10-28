package io.github.dschonas04.managr.stumm;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.core.Filter;
import org.apache.logging.log4j.core.LoggerContext;
import org.apache.logging.log4j.core.filter.RegexFilter;

/** Blendet reinen Log-Müll aus, der sonst die Konsole flutet. */
final class LogFilter {
    private LogFilter() {}

    static void install() {
        try {
            add();
        } catch (Exception | LinkageError e) {
            LogManager.getLogger("stumm").warn("Log-Filter nicht aktiv: {}", e.toString());
        }
    }

    private static void add() throws Exception {
        LoggerContext context = (LoggerContext) LogManager.getContext(false);
        Filter filter = RegexFilter.createFilter("Invalid entity rotation: NaN.*", null, false, Filter.Result.DENY, Filter.Result.NEUTRAL);
        filter.start();
        context.getConfiguration().addFilter(filter);
        context.updateLoggers();
    }
}
