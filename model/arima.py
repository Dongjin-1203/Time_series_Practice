from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
import matplotlib.pyplot as plt
from pmdarima import auto_arima
from sklearn.metrics import mean_squared_error
import numpy as np
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX


# 경고 무시
import warnings
warnings.filterwarnings("ignore")

os.makedirs("model/(Auto)ARIMA", exist_ok=True)
os.makedirs("model/SARIMA", exist_ok=True)
class Time_series:

    def __init__(self, train_final_data: pd.DataFrame):
        # 데이터 준비
        self.df = train_final_data.copy()
        self.df['Date'] = pd.to_datetime(self.df['Date'])

        self.store_ids = self.df['Store'].unique()
        self.store_depts = self.df['Dept'].unique()

    def arima(self, forecast_steps=12):
        # 매장별 부서별 데이터 정재
        for (store_id, store_dept), group in self.df.groupby(['Store', 'Dept']):
            # 주간 매출 시계열만 추출
            ts = group.set_index('Date')['Weekly_Sales']

            if ts.shape[0] < 60:
                print(f"Skipping Store {store_id}, Dept {store_dept} (insufficient data)")
                continue
            
            try:
                #시각화 및 정상성 확인
                plt.figure(figsize=(12, 5))
                ts.plot()
                plt.title(f"Store {store_id} - Dept {store_dept} Weekly Sales")
                plt.ylabel("Weekly Sales")
                plt.grid(True)
                # plt.show()

                # 모델 학습
                #model = ARIMA(ts, order=(1, 1, 1))  # (p, d, q)
                #model_fit = model.fit()
                #print(model_fit.summary())

                # Auto ARIMA(데이터 한마당 경진대회 미사용: 사유{라이브러리 미지원})
                auto_model = auto_arima(ts, seasonal=False, stepwise=True, suppress_warnings=True)
                print(auto_model.summary())

                # 향후 (steps=12)주 예측(ARIMA)
                # forecast = model_fit.forecast(steps=12)

                # 향후 (steps=12)주 예측(ARIMA)
                forecast = auto_model.predict(n_periods=forecast_steps)
                #print(forecast.head())

                plt.figure(figsize=(12,5))
                ts.plot(label='Observed')
                forecast.plot(label='Forecast', linestyle='--')
                plt.legend()
                plt.title(f"Store {store_id} - Dept {store_dept} ARIMA Forecast (Next {forecast_steps} Weeks)")
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(f"model/(Auto)ARIMA/Store {store_id} - Dept {store_dept} ARIMA Forecast (Next {forecast_steps} Weeks).png", dpi=300)
                plt.close()
                #plt.show()

                forecast = pd.DataFrame(forecast)
                forecast.to_csv(f"model/(Auto)ARIMA/Store {store_id} - Dept {store_dept} ARIMA Forecast (Next {forecast_steps} Weeks)_train_result.csv", 
                                index=False, 
                                encoding='utf-8-sig'
                                )

                """
                # 예측 기간에 해당하는 실제 값이 있다면 비교
                # 예시: train/test 나눠서 진행하는 방식

                mse = mean_squared_error(actual, forecast)
                print(f"RMSE: {np.sqrt(mse):.2f}")
                """
            except Exception as e:
                print(f"Error on Store {store_id}, Dept {store_dept}: {e}")

    def sarima(self, forecast_steps=12):
        # 매장별 부서별 데이터 정재
        for (store_id, store_dept), group in self.df.groupby(['Store', 'Dept']):
            # 주간 매출 시계열만 추출
            ts = group.set_index('Date')['Weekly_Sales']

            if ts.shape[0] < 60:
                print(f"Skipping Store {store_id}, Dept {store_dept} (insufficient data)")
                continue
            
            try:
                # SARIMA 파라미터 자동 추천
                auto_model = auto_arima(
                            ts,
                            seasonal=True,
                            m=52,
                            stepwise=True,
                            suppress_warnings=True,
                            error_action='ignore'
                            )

                order = auto_model.order
                seasonal_order = auto_model.seasonal_order

                # 모델 재학습
                model = SARIMAX(ts, order=order, seasonal_order=seasonal_order)
                model_fit = model.fit()

                # 예측
                forecast = model_fit.forecast(forecast_steps)

                # 시각화
                plt.figure(figsize=(10, 4))
                ts.plot(label='Observed')
                forecast.plot(label='Forecast', linestyle='--')
                plt.title("SARIMA Forecast")
                plt.legend()
                plt.grid(True)
                plt.tight_layout()
                plt.savefig(f"model/SARIMA/Store {store_id} - Dept {store_dept} ARIMA Forecast (Next {forecast_steps} Weeks).png", dpi=300)
                plt.close()

                forecast = pd.DataFrame(forecast)
                forecast.to_csv(f"model/SARIMA/Store {store_id} - Dept {store_dept} ARIMA Forecast (Next {forecast_steps} Weeks)_train_result.csv", 
                                index=False, 
                                encoding='utf-8-sig'
                                )
                
                """
                # 예측 기간에 해당하는 실제 값이 있다면 비교
                # 예시: train/test 나눠서 진행하는 방식

                mse = mean_squared_error(actual, forecast)
                print(f"RMSE: {np.sqrt(mse):.2f}")
                """

            except Exception as e:
                print(f"Error on Store {store_id}, Dept {store_dept}: {e}")