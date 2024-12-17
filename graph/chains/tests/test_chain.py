from graph.chains.search_query_generator import search_string_generator
from graph.chains.alert_threshold_generator import alert_threshold_generator, AlertThreshold

def test_search_sting_generator_yes() -> None:
    metric_name = "oracle tablespace data_file size free bytes"
    metric_description="the size of the file available for user data. The actual size of the file minus this value is used to store file related metadata."
    res = search_string_generator.invoke({
        "metric_name": metric_name,
        "metric_description": metric_description
    })
    print(res.search_string)
    assert res.search_string

def test_alert_threshold_generator_no() -> None:
    research_document = """I do not know how to make pizza"""

    res: AlertThreshold = alert_threshold_generator.invoke({
        "research_document": research_document
    })

    # Assertions to check for absence of thresholds
    assert res.warning_threshold == -1, "Expected warning_threshold to be -1 when threshold is absent."
    assert res.critical_threshold == -1, "Expected critical_threshold to be -1 when threshold is absent."
    assert res.is_threshold_available == False, "Expected is_threshold_available to be False when thresholds are absent."
    
    # Type assertions
    assert isinstance(res.warning_threshold, float), "Expected warning_threshold to be of type float."
    assert isinstance(res.critical_threshold, float), "Expected critical_threshold to be of type float."
    assert isinstance(res.is_threshold_available, bool), "Expected is_threshold_available to be of type bool."
    
    print(res.research_references)
    

def test_alert_threshold_generator_yes() -> None:
    research_document = """
    # Oracle Tablespace Monitoring: Observability and Alert Configuration

## Introduction

Oracle databases are widely used in enterprise environments for their robustness and scalability. One of the critical aspects of managing an Oracle database is monitoring tablespaces, which are logical storage units that hold data files. Effective monitoring ensures that the database operates efficiently and prevents potential issues such as running out of space. This report delves into the intricacies of Oracle tablespace monitoring, focusing on data file size, free bytes, observability, alert configuration, and the suitability of these configurations for user data availability and free space threshold management.

## Understanding Oracle Tablespaces

### Tablespace Structure

An Oracle tablespace is a logical storage unit that consists of one or more data files. These data files are physical files on disk that store the actual data. Tablespaces can be of different types, such as permanent, temporary, and undo tablespaces, each serving specific purposes within the database environment ([Oracle Docs](https://docs.oracle.com/en/database/oracle/oracle-database/18/spuss/set-threshold-values-for-tablespace-alerts.html)).

### Data File Size and Free Bytes

Monitoring the size of data files and the available free bytes is crucial for maintaining the health of the database. As data is inserted or updated, the space within these data files is consumed. If a data file reaches its maximum size, it can lead to performance degradation or even downtime if not managed properly. Therefore, understanding the current utilization and available free space is essential for proactive database management ([Database Journal](https://www.databasejournal.com/oracle/monitoring-tablespace-usage-in-oracle/)).

## Observability and Monitoring

### Importance of Observability

Observability in databases refers to the ability to monitor and understand the internal states of the system based on the data it generates. For Oracle databases, this involves tracking metrics such as tablespace usage, data file sizes, and free space availability. Effective observability allows database administrators (DBAs) to detect anomalies, predict potential issues, and take corrective actions before they impact the system ([PowerAdmin](https://www.poweradmin.com/blog/best-practices-for-monitoring-oracle-database/)).

### Monitoring Tools and Techniques

Oracle provides several tools and techniques for monitoring tablespace usage:

1. **Enterprise Manager (EM):** A comprehensive tool that offers a graphical interface for monitoring and managing Oracle databases. It provides alerts and reports on tablespace usage and other critical metrics ([Oracle Forums](https://forums.oracle.com/ords/apexds/community/q?question=tablespace-alerting-threshold-for-large-tablespaces-2982)).

2. **SQL Queries:** Custom SQL queries can be used to extract detailed information about tablespace usage. For example, querying the `DBA_FREE_SPACE` view can provide insights into the free space available in each tablespace ([Stack Overflow](https://stackoverflow.com/questions/7672126/find-out-free-space-on-tablespace)).

3. **DBMS_SERVER_ALERT Package:** This package allows DBAs to set thresholds for tablespace usage and receive alerts when these thresholds are crossed. It is a proactive approach to managing space issues ([Oracle-Base](https://oracle-base.com/articles/misc/tablespace-thresholds-and-alerts)).

## Alert Configuration and Suitability

### Threshold Values for Alerts

Setting appropriate threshold values for tablespace alerts is crucial for effective monitoring. Oracle recommends default threshold values of 85% for warnings and 97% for critical alerts. These values can be adjusted based on the specific requirements of the database environment ([Oracle Docs](https://docs.oracle.com/en/database/oracle/oracle-database/18/spuss/set-threshold-values-for-tablespace-alerts.html)).

### Configuring Alerts

Alerts can be configured to notify DBAs when tablespace usage crosses predefined thresholds. This configuration can be done using Oracle Enterprise Manager or through SQL scripts that utilize the `DBMS_SERVER_ALERT` package. Alerts can be set for both percentage-based thresholds and absolute free space thresholds, depending on the size and nature of the tablespace ([Oracle Forums](https://forums.oracle.com/ords/apexds/post/tablespace-threshold-alert-2377)).

### Suitability for User Data Availability

The configuration of tablespace alerts must ensure that user data remains available and that the database operates without interruptions. For large tablespaces, percentage-based thresholds might not be sufficient, as a small percentage of free space could still represent a significant amount of unused space. In such cases, absolute free space thresholds are more suitable. For example, a 1TB tablespace might have a threshold set to alert when free space falls below 100GB, ensuring ample space for data growth ([Oracle Forums](https://forums.oracle.com/ords/apexds/community/q?question=tablespace-alerting-threshold-for-large-tablespaces-2982)).

## Challenges and Best Practices

### Challenges in Monitoring

1. **Dynamic Workloads:** Oracle databases often support dynamic workloads, making it challenging to predict space usage accurately. This requires adaptive monitoring strategies that can adjust thresholds based on usage patterns.

2. **Autoextensible Data Files:** While autoextensible data files can help manage space automatically, they can also lead to unexpected storage consumption if not monitored closely. It is essential to track the growth of these files and adjust thresholds accordingly ([Orahhow](https://orahow.com/tablespace-utilization-in-oracle/)).

### Best Practices

1. **Regular Monitoring:** Implement regular monitoring schedules to track tablespace usage and adjust thresholds as needed. This helps in identifying trends and planning for future storage needs.

2. **Combining Metrics:** Use a combination of size and percentage thresholds to get a comprehensive view of tablespace usage. This approach ensures that both small and large tablespaces are monitored effectively ([PowerAdmin](https://www.poweradmin.com/blog/best-practices-for-monitoring-oracle-database/)).

3. **Proactive Alerts:** Configure alerts to not only notify when thresholds are crossed but also to trigger automated actions, such as adding space or archiving old data, to prevent issues from escalating.

## Conclusion

Monitoring Oracle tablespaces is a critical aspect of database management that ensures data availability and system performance. By understanding the structure of tablespaces, utilizing effective monitoring tools, and configuring suitable alert thresholds, DBAs can proactively manage space and prevent potential issues. The combination of observability, alert configuration, and best practices forms a robust framework for maintaining the health and efficiency of Oracle databases.

## References

Database Journal. (2015, June 11). Monitoring Tablespace Usage in Oracle. Database Journal. https://www.databasejournal.com/oracle/monitoring-tablespace-usage-in-oracle/

Oracle Docs. (n.d.). Set Threshold Values for Tablespace Alerts. Oracle. https://docs.oracle.com/en/database/oracle/oracle-database/18/spuss/set-threshold-values-for-tablespace-alerts.html

Oracle Forums. (2022, May 11). Tablespace alerting threshold for large tablespaces. Oracle Forums. https://forums.oracle.com/ords/apexds/community/q?question=tablespace-alerting-threshold-for-large-tablespaces-2982

Oracle-Base. (n.d.). Tablespace Thresholds and Alerts (DBMS_SERVER_ALERT). Oracle-Base. https://oracle-base.com/articles/misc/tablespace-thresholds-and-alerts

Orahhow. (n.d.). Tablespace Utilization In Oracle Multitenant Database. Orahhow. https://orahow.com/tablespace-utilization-in-oracle/

PowerAdmin. (n.d.). Best Practices for Monitoring Oracle Database. Network Wrangler – Tech Blog. https://www.poweradmin.com/blog/best-practices-for-monitoring-oracle-database/

Stack Overflow. (2013, February 25). oracle database - Find out free space on tablespace. Stack Overflow. https://stackoverflow.com/questions/7672126/find-out-free-space-on-tablespace
    """
    res = alert_threshold_generator.invoke({
        "research_document": research_document
    })
    # Assert that the warning threshold is a positive value, indicating a valid threshold was extracted
    assert(res.warning_threshold > 0)

    # Assert that the critical threshold is a positive value, confirming a valid threshold was extracted
    assert(res.critical_threshold > 0)

    # Assert that the `is_threshold_available` flag is True, indicating at least one threshold was found in the document
    assert(res.is_threshold_available == True)

    # Check that the warning threshold is of type float, ensuring correct data type
    assert(isinstance(res.warning_threshold, float))

    # Check that the critical threshold is of type float, ensuring correct data type
    assert(isinstance(res.critical_threshold, float))

    # Confirm that `is_threshold_available` is of type bool, ensuring correct data type
    assert(isinstance(res.is_threshold_available, bool))
    
    print(res.research_references)
    
