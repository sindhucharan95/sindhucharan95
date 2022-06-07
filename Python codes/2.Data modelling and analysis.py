## Import relevant packages
import pandas as pd

##Import data
path = "/Users/systemuserpath/Filepath"
Transactions = pd.read_csv(f"{path}/TransactionsData.txt", sep="|", header=0, doublequote=None,
                           dtype={'USERID': 'string'})
Custdata = pd.read_csv(f"{path}/CustomerData.txt", sep="|", header=0, doublequote=None, dtype={'USERID': 'string'})
Itemdata = pd.read_csv(f"{path}/ItemData.txt", sep="|", header=0, doublequote=None, dtype={'ITEM': 'string'})

# Check data types in imported data

print(Transactions.dtypes)
print(Custdata.dtypes)
print(Itemdata.dtypes)

# Check for duplicates in the Primary key columns and summarize if there are any duplicates
print(Custdata['USERID'].is_unique)  # There are no duplicates
print(Itemdata['ITEM'].is_unique)  # There are duplicates in the Item column and needs to be un-duplicated

# # Removing duplicates on  Item data on ITEM,CATEGORY,COLOR,PURCHASEPRICE,SALEPRICE and drop the duplicating column
# SUPLID
Item_summ = Itemdata.drop_duplicates(subset=['ITEM', 'CATEGORY', 'COLOR', 'PURCHASEPRICE', 'SALEPRICE']).drop(
    ['SUPLID'], axis=1)
print(Item_summ)


## Combinining the three datasets into a single reusable model based on the data dictionary
def Main_data(Tr, Cu, It):
    Main_data = pd.merge(Tr, Cu, on='USERID', how='left')
    Main_data = pd.merge(Main_data, It, on='ITEM', how='left')
    return Main_data


Combined_data = Main_data(Transactions, Custdata, Item_summ)

## Create additional columns for analysis and change data types of imported columns(if necessary)

Combined_data['PURCHASEPRICE'] = Combined_data['PURCHASEPRICE'].astype('float')
Combined_data['SALEPRICE'] = Combined_data['SALEPRICE'].astype('float')
Combined_data['QTY'] = Combined_data['QTY'].replace({' ': '0'}).astype('int')
Combined_data['DISCOUNT'] = Combined_data['DISCOUNT'].replace({' ': '0'}).astype('int')
Combined_data['SHIPDAYS'] = Combined_data['SHIPDAYS'].replace({' ': '0'}).astype('int')
Combined_data['Originalprice'] = Combined_data['SALEPRICE'] / (1 - (Combined_data['DISCOUNT']) / 100)
Combined_data['Salesamt'] = Combined_data['SALEPRICE'] * Combined_data['QTY']
Combined_data['DiscountAmt'] = (Combined_data['Salesamt'] / (1 - (Combined_data['DISCOUNT']) / 100)) - Combined_data[
    'Salesamt']
Combined_data['Cost'] = Combined_data['PURCHASEPRICE'] * Combined_data['QTY']
Combined_data['Margin'] = Combined_data['Salesamt'] - Combined_data['Cost']
Combined_data['Deliverymnth'] = Combined_data['DELIVERYDATE'].str[5:6].str.rjust(2, "0")
print(Combined_data)  ##60.000 rows and 30 columns
print(Combined_data.dtypes)

## R01 Missing Values-check for null values in  columns

R01 = ((Combined_data.isnull() | Combined_data.eq(' '))).sum()


# R02 Top-10 Reports-Choose a column on which top 10 analysis based on Sales is to be performed
def R02(Combined_data):
    Top10 = 'USERID'
    return pd.DataFrame(Combined_data.groupby(Top10)['Salesamt'].sum())['Salesamt'].nlargest(10, keep='all')


R02 = R02(Combined_data)
# R03 Transactions with negative gross margin
R03 = Combined_data.where(Combined_data['Margin'] < 0.00)
print(R03)


# R04 Transactions not complete but deliveries were made
def R04(Combined_data):
    return Combined_data.where(Combined_data['PURCHASE'] == 'NO') & (Combined_data['DELIVERYDATE'].notnull())


R04 = R04(Combined_data)


# R05 Items with highest sales and margins
def R05a(Combined_data):
    return pd.DataFrame(Combined_data.groupby('CATEGORY')['Salesamt'].sum())


R05a = R05a(Combined_data)


def R05b(Combined_data):
    return pd.DataFrame(Combined_data.groupby('CATEGORY')['Margin'].sum())


R05b = R05b(Combined_data)


# R06 PPC's Responsible for highest sales ,margins and discounts
def R06a(Combined_data):
    return pd.DataFrame(Combined_data.groupby('PPC_ADD')['Salesamt'].sum())


R06a = R06a(Combined_data)


def R06b(Combined_data):
    return pd.DataFrame(Combined_data.groupby('PPC_ADD')['Margin'].sum())


R06b = R06b(Combined_data)


def R06c(Combined_data):
    R06c = pd.DataFrame(Combined_data.groupby('PPC_ADD')[['DiscountAmt', 'Salesamt']].sum())
    R06c['Discount%'] = (R06c['DiscountAmt'] / R06c['Salesamt']) * 100
    return R06c


R06c = R06c(Combined_data)


# R07 Month on Month trend on sales

def R07(Combined_data):
    return pd.DataFrame(Combined_data.groupby('Deliverymnth')['Salesamt'].sum())


R07 = R07(Combined_data)

##Exporting the reports
with pd.ExcelWriter(f'{path}/Exceptions report.xlsx') as writer:
    R01.to_excel(writer, sheet_name='R01', index=True, header=True)
    R02.to_excel(writer, sheet_name='R02', index=True, header=True)
    R03.to_excel(writer, sheet_name='R03', index=False, header=True)
    R04.to_excel(writer, sheet_name='R04', index=True, header=True)
    R05a.to_excel(writer, sheet_name='R05a', index=True, header=True)
    R05b.to_excel(writer, sheet_name='R05b', index=True, header=True)
    R06a.to_excel(writer, sheet_name='R06a', index=True, header=True)
    R06b.to_excel(writer, sheet_name='R06b', index=True, header=True)
    R06c.to_excel(writer, sheet_name='R06c', index=True, header=True)
    R07.to_excel(writer, sheet_name='R07', index=True, header=True)
