#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 22:28:09 2019

@author: abazbaz
"""

def df_to_table(df):
    table_str = """
    <table class="table table-bordered table-striped table-hover js-basic-example dataTable">
                              <thead>
                                  <tr>
                                      <th>ID</th>
                                      <th>Cliente</th>
                                      <th>Fecha programada</th>
                                      <th>Fecha de vencimiento</th>
                                      <th>Monto</th>
                                      <th>Referencia</th>
                                      <th>Status</th>
                                      <th>Acciones</th>
                                  </tr>
                              </thead>
                              <tfoot>
                                  <tr>
                                    <th>ID</th>
                                    <th>Cliente</th>
                                    <th>Fecha programada</th>
                                    <th>Fecha de vencimiento</th>
                                    <th>Monto</th>
                                    <th>Referencia</th>
                                    <th>Status</th>
                                    <th>Acciones</th>
                                  </tr>
                              </tfoot>
                              <tbody>
                                  <tr>
                                      <td>1</td>
                                      <td>Felxi</td>
                                      <td>14/06/2018</td>
                                      <td>21/12/2018</td>
                                      <td>$320,800</td>
                                      <td>Abc138Gs</td>
                                      <td> <span class="badge bg-red">Incompleto</span></td>
                                      <td>
                                        <a class="btn btn-xs btn-info waves-effect" href="/ingresos/perfil_ingreso" data-toggle="tooltip" data-placement="top" title="Ver detalle">
                                            <i class="material-icons">visibility</i>
                                        </a>
                                        <a class="btn js-modal-buttons btn-xs btn-success waves-effect" data-toggle="modal" data-target="#modal_cobrar" >
                                            <i data-toggle="tooltip" data-placement="top" title="Marcar como Recibido" class="material-icons">payment</i>
                                        </a>
                                      </td>
                                  </tr>
                              </tbody>
                          </table>"""
                         
    return table_str
                      